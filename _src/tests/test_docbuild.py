from pathlib import Path
from unittest.mock import patch


from docbuild import DocumentDiscovery, FrontmatterReader, SiteBuilder


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


def test_build_renders_documents_and_copies_static_files(tmp_path: Path) -> None:
    (tmp_path / "_templates").mkdir()
    (tmp_path / "_templates" / "page.template").write_text(
        "<title>{{ page.title }}</title>{{ content }}", encoding="utf-8"
    )
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "page.md").write_text(
        "---\ntitle: Hello\n---\n\n# Body", encoding="utf-8"
    )
    (tmp_path / "assets.txt").write_text("asset", encoding="utf-8")

    with patch("docbuild.pypandoc.convert_text", return_value="<h1>Body</h1>"):
        SiteBuilder(tmp_path).build()

    assert (tmp_path / "_site" / "nested" / "page.html").read_text(encoding="utf-8") == (
        "<title>Hello</title><h1>Body</h1>"
    )
    assert (tmp_path / "_site" / "assets.txt").read_text(encoding="utf-8") == "asset"
