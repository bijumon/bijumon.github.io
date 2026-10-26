from datetime import date
from pathlib import Path
from unittest.mock import patch

import dbm.sqlite3
import json
import pytest

from docbuild import BuildError, DocumentDiscovery, FileCache, FrontmatterReader, SiteBuilder


def _site(tmp_path: Path, template: str = "<title>{{ page.title }}</title>{{ content }}") -> None:
    (tmp_path / "_templates").mkdir(exist_ok=True)
    (tmp_path / "_templates" / "page.template").write_text(template, encoding="utf-8")


def test_discovery_ignores_dot_and_underscore_paths(tmp_path: Path) -> None:
    (tmp_path / "page.md").write_text("# Page", encoding="utf-8")
    (tmp_path / "visible.txt").write_text("asset", encoding="utf-8")
    (tmp_path / ".hidden.md").write_text("ignored", encoding="utf-8")
    (tmp_path / "_drafts").mkdir()
    (tmp_path / "_drafts" / "draft.md").write_text("ignored", encoding="utf-8")

    discovery = DocumentDiscovery(tmp_path)
    assert [p.name for p in discovery.documents()] == ["page.md"]
    assert [p.name for p in discovery.static_files()] == ["visible.txt"]


def test_reads_yaml_frontmatter(tmp_path: Path) -> None:
    source = tmp_path / "page.md"
    source.write_text("---\ntitle: Hello\n---\n\n# Body\n", encoding="utf-8")

    metadata, body = FrontmatterReader().read(source)

    assert metadata["title"] == "Hello"
    assert "# Body" in body


def test_reads_toml_frontmatter(tmp_path: Path) -> None:
    source = tmp_path / "page.md"
    source.write_text("+++\ntitle = 'Hello'\n+++\n\n# Body\n", encoding="utf-8")

    metadata, body = FrontmatterReader().read(source)

    assert metadata["title"] == "Hello"
    assert "# Body" in body


def test_rejects_missing_frontmatter_closing_delimiter(tmp_path: Path) -> None:
    source = tmp_path / "page.md"
    source.write_text("---\ntitle: Hello\n# Body\n", encoding="utf-8")

    with pytest.raises(BuildError, match="missing closing"):
        FrontmatterReader().read(source)


def test_build_renders_documents_and_copies_static_files(tmp_path: Path) -> None:
    _site(tmp_path)
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "page.md").write_text(
        "---\ntitle: Hello\n---\n\n# Body", encoding="utf-8"
    )
    (tmp_path / "assets.txt").write_text("asset", encoding="utf-8")

    with patch("docbuild.converter.pypandoc.convert_text", return_value="<h1>Body</h1>"):
        SiteBuilder(tmp_path).build()

    assert (tmp_path / "_site" / "nested" / "page.html").read_text(encoding="utf-8") == (
        "<title>Hello</title><h1>Body</h1>"
    )
    assert (tmp_path / "_site" / "assets.txt").read_text(encoding="utf-8") == "asset"


def test_detects_document_output_collisions(tmp_path: Path) -> None:
    (tmp_path / "page.md").write_text("# Markdown", encoding="utf-8")
    (tmp_path / "page.djot").write_text("Djot", encoding="utf-8")

    with pytest.raises(BuildError, match="output collision"):
        SiteBuilder(tmp_path).build()


def test_unchanged_document_is_not_converted_twice(tmp_path: Path) -> None:
    _site(tmp_path)
    (tmp_path / "page.md").write_text("---\ntitle: Hello\n---\n\n# Body", encoding="utf-8")

    with patch("docbuild.converter.pypandoc.convert_text", return_value="<h1>Body</h1>") as convert:
        SiteBuilder(tmp_path).build()
        SiteBuilder(tmp_path).build()

    assert convert.call_count == 1


def test_changed_document_is_rebuilt(tmp_path: Path) -> None:
    _site(tmp_path)
    source = tmp_path / "page.md"
    source.write_text("---\ntitle: One\n---\n\n# First", encoding="utf-8")

    with patch(
        "docbuild.converter.pypandoc.convert_text",
        side_effect=["<h1>First</h1>", "<h1>Second</h1>"],
    ) as convert:
        SiteBuilder(tmp_path).build()
        source.write_text("---\ntitle: Two\n---\n\n# Second and longer", encoding="utf-8")
        SiteBuilder(tmp_path).build()

    assert convert.call_count == 2
    output = (tmp_path / "_site" / "page.html").read_text(encoding="utf-8")
    assert "<title>Two</title>" in output
    assert "<h1>Second</h1>" in output


def test_static_files_are_not_recopied_when_unchanged(tmp_path: Path) -> None:
    (tmp_path / "asset.txt").write_text("asset", encoding="utf-8")
    with patch("docbuild.builder.shutil.copy2", wraps=__import__("shutil").copy2) as copy:
        SiteBuilder(tmp_path).build()
        copy.reset_mock()
        SiteBuilder(tmp_path).build()
    copy.assert_not_called()


def test_missing_output_is_regenerated_even_when_source_is_unchanged(tmp_path: Path) -> None:
    _site(tmp_path)
    (tmp_path / "page.md").write_text("# Body", encoding="utf-8")

    with patch("docbuild.converter.pypandoc.convert_text", return_value="<h1>Body</h1>") as convert:
        SiteBuilder(tmp_path).build()
        (tmp_path / "_site" / "page.html").unlink()
        SiteBuilder(tmp_path).build()
    assert convert.call_count == 2


def test_template_change_rebuilds_documents(tmp_path: Path) -> None:
    _site(tmp_path)
    (tmp_path / "page.md").write_text("---\ntitle: Hello\n---\n\n# Body", encoding="utf-8")

    with patch("docbuild.converter.pypandoc.convert_text", return_value="<h1>Body</h1>") as convert:
        SiteBuilder(tmp_path).build()
        (tmp_path / "_templates" / "page.template").write_text(
            "<h1>{{ page.title }}</h1>{{ content }}", encoding="utf-8"
        )
        SiteBuilder(tmp_path).build()
    assert convert.call_count == 2


def test_failed_conversion_is_retried(tmp_path: Path) -> None:
    _site(tmp_path)
    (tmp_path / "page.md").write_text("# Body", encoding="utf-8")

    with patch("docbuild.converter.pypandoc.convert_text", side_effect=RuntimeError("failure")):
        with pytest.raises(BuildError, match="conversion failed"):
            SiteBuilder(tmp_path).build()

    with patch("docbuild.converter.pypandoc.convert_text", return_value="<h1>Body</h1>") as convert:
        SiteBuilder(tmp_path).build()
    assert convert.call_count == 1


def test_deleted_source_is_marked_and_output_is_retained(tmp_path: Path) -> None:
    _site(tmp_path)
    source = tmp_path / "page.md"
    source.write_text("# Body", encoding="utf-8")
    with patch("docbuild.converter.pypandoc.convert_text", return_value="<h1>Body</h1>"):
        SiteBuilder(tmp_path).build()

    output = tmp_path / "_site" / "page.html"
    assert output.is_file()
    source.unlink()
    SiteBuilder(tmp_path).build()
    assert output.is_file()

    with FileCache(tmp_path / ".cache.db") as cache:
        record = cache.get("page.md")
    assert record is not None
    assert record["deleted"] is True


def test_cache_preserves_frontmatter_date_types(tmp_path: Path) -> None:
    with FileCache(tmp_path / ".cache.db") as cache:
        cache.set("date.md", {"frontmatter": {"published": date(2026, 10, 25)}})
        record = cache.get("date.md")
    assert record is not None
    assert record["frontmatter"]["published"] == date(2026, 10, 25)


def test_dbm_sqlite_cache_contains_serialized_records(tmp_path: Path) -> None:
    with FileCache(tmp_path / ".cache.db") as cache:
        cache.set("page.md", {"kind": "document"})
    database = dbm.sqlite3.open(str(tmp_path / ".cache.db"), "r")
    try:
        assert b"file:page.md" in database
        assert json.loads(database[b"file:page.md"].decode("utf-8")) == {"kind": "document"}
    finally:
        database.close()


def test_site_pages_are_available_to_jinja_filters(tmp_path: Path) -> None:
    _site(
        tmp_path,
        template=(
            '<p id="count">{{ site.pages | count }}</p>'
            '<ul>{% for item in site.pages | reverse %}'
            '<li>{{ item.title }}|{{ item.source }}|{{ item.url }}</li>'
            "{% endfor %}</ul>{{ content }}"
        ),
    )
    (tmp_path / "alpha.md").write_text("---\ntitle: Alpha\n---\n\nAlpha", encoding="utf-8")
    (tmp_path / "notes").mkdir()
    (tmp_path / "notes" / "beta.md").write_text(
        "---\ntitle: Beta\n---\n\nBeta", encoding="utf-8"
    )

    with patch("docbuild.converter.pypandoc.convert_text", side_effect=["<p>Alpha</p>", "<p>Beta</p>"]):
        SiteBuilder(tmp_path).build()

    output = (tmp_path / "_site" / "alpha.html").read_text(encoding="utf-8")
    assert '<p id="count">2</p>' in output
    assert output.index("Beta|notes/beta.md|notes/beta.html") < output.index(
        "Alpha|alpha.md|alpha.html"
    )


def test_site_page_catalog_change_rebuilds_unchanged_pages(tmp_path: Path) -> None:
    _site(
        tmp_path,
        template=(
            "{% for item in site.pages %}<span>{{ item.title }}</span>{% endfor %}"
            "{{ content }}"
        ),
    )
    alpha = tmp_path / "alpha.md"
    beta = tmp_path / "beta.md"
    alpha.write_text("---\ntitle: Alpha\n---\n\nAlpha", encoding="utf-8")
    beta.write_text("---\ntitle: Beta\n---\n\nBeta", encoding="utf-8")

    with patch("docbuild.converter.pypandoc.convert_text", return_value="<p>Content</p>") as convert:
        SiteBuilder(tmp_path).build()
        beta.write_text("---\ntitle: Bravo Updated\n---\n\nBeta", encoding="utf-8")
        SiteBuilder(tmp_path).build()

    # Both pages rebuild: beta changed, and alpha's site.pages data changed.
    assert convert.call_count == 4
    alpha_output = (tmp_path / "_site" / "alpha.html").read_text(encoding="utf-8")
    assert "Bravo Updated" in alpha_output


def test_markdown_conversion_uses_commonmark_reader(tmp_path: Path) -> None:
    from docbuild.converter import DocumentConverter

    source = tmp_path / "page.md"
    with patch("docbuild.converter.pypandoc.convert_text", return_value="<pre><code></code></pre>") as convert:
        DocumentConverter().convert(source, "```python\nprint('hello')\n```")

    assert convert.call_args.kwargs["format"] == "commonmark"
