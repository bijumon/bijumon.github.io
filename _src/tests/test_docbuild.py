from datetime import date
from pathlib import Path
from unittest.mock import patch

import dbm.sqlite3
import json
import os
import subprocess
import sys
import pytest

from docbuild import (
    BuildArtifact,
    BuildError,
    BuildGraph,
    BuildPlanner,
    DocumentDiscovery,
    FileCache,
    FrontmatterReader,
    SiteBuilder,
)
from docbuild.config import CONFIG_DEFAULTS, load_config
from docbuild.timestamp_restore import restore_source_timestamps


def _site(tmp_path: Path, template: str = "<title>{{ page.title }}</title>{{ content }}") -> None:
    (tmp_path / "_templates").mkdir(exist_ok=True)
    (tmp_path / "_templates" / "page.template").write_text(template, encoding="utf-8")


def _create_symlink(link: Path, target: Path, *, target_is_directory: bool = False) -> None:
    try:
        link.symlink_to(target, target_is_directory=target_is_directory)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"symbolic links are not supported in this environment: {exc}")




@pytest.fixture(autouse=True)
def _provide_site_config(tmp_path: Path) -> None:
    """Keep ordinary build tests representative of a configured site root."""
    (tmp_path / "_config.toml").write_text(
        'author = "Biju Punalor"\n'
        'name = "Notes"\n'
        'description = "Personal website and notes."\n'
        'url = "https://bijumon.github.io"\n'
        'language = "en"\n'
        'generator = "docbuild.py"\n',
        encoding="utf-8",
    )


def test_config_defaults_are_generic_nonempty_strings() -> None:
    expected = {
        "author": "Unknown Author",
        "name": "Untitled Site",
        "description": "A website built with docbuild.",
        "url": "https://example.com",
        "language": "en",
        "generator": "docbuild",
        "content_hash_max_bytes": 100 * 1024 * 1024,
    }
    assert {key: CONFIG_DEFAULTS[key] for key in expected} == expected
    assert all(
        isinstance(value, str) and value.strip()
        for key, value in CONFIG_DEFAULTS.items()
        if key != "content_hash_max_bytes"
    )


def test_config_uses_defaults_when_toml_is_empty(tmp_path: Path) -> None:
    (tmp_path / "_config.toml").write_text("", encoding="utf-8")

    assert load_config(tmp_path) == CONFIG_DEFAULTS


@pytest.mark.parametrize("value", ['"100"', "-1", "true", "1.5"])
def test_config_rejects_invalid_content_hash_max_bytes(tmp_path: Path, value: str) -> None:
    (tmp_path / "_config.toml").write_text(
        f"content_hash_max_bytes = {value}\n",
        encoding="utf-8",
    )

    with pytest.raises(BuildError, match="content_hash_max_bytes must be a non-negative integer"):
        load_config(tmp_path)


def test_config_toml_overrides_defaults_and_preserves_unspecified_values(
    tmp_path: Path,
) -> None:
    (tmp_path / "_config.toml").write_text(
        'name = "Configured Notes"\n'
        'url = "https://example.test"\n'
        'content_hash_max_bytes = 4096\n',
        encoding="utf-8",
    )

    config = load_config(tmp_path)

    assert config["name"] == "Configured Notes"
    assert config["url"] == "https://example.test"
    assert config["author"] == CONFIG_DEFAULTS["author"]
    assert config["description"] == CONFIG_DEFAULTS["description"]
    assert config["language"] == CONFIG_DEFAULTS["language"]
    assert config["content_hash_max_bytes"] == 4096


def test_build_rejects_missing_config_file(tmp_path: Path) -> None:
    (tmp_path / "_config.toml").unlink()

    with pytest.raises(BuildError, match="required configuration file not found"):
        SiteBuilder(tmp_path).build()


def test_build_reports_invalid_config_toml(tmp_path: Path) -> None:
    (tmp_path / "_config.toml").write_text('name = "unterminated\n', encoding="utf-8")

    with pytest.raises(BuildError, match="invalid TOML in configuration file"):
        SiteBuilder(tmp_path).build()


def test_site_metadata_from_config_is_available_to_templates(tmp_path: Path) -> None:
    _site(
        tmp_path,
        template=(
            "<title>{{ site.name }}</title>"
            "<p>{{ site.description }}</p>"
            '<p id="internal-config">{{ site.content_hash_max_bytes | default("not-exposed") }}</p>'
            "{{ content }}"
        ),
    )
    (tmp_path / "_config.toml").write_text(
        'name = "Configured Notes"\n'
        'description = "Loaded from TOML."\n',
        encoding="utf-8",
    )
    (tmp_path / "page.md").write_text("# Body", encoding="utf-8")

    with patch("docbuild.converter.pypandoc.convert_text", return_value="<h1>Body</h1>"):
        SiteBuilder(tmp_path).build()

    output = (tmp_path / "_site" / "page.html").read_text(encoding="utf-8")
    assert output == (
        "<title>Configured Notes</title><p>Loaded from TOML.</p>"
        '<p id="internal-config">not-exposed</p><h1>Body</h1>'
    )


def test_discovery_ignores_dot_and_underscore_paths(tmp_path: Path) -> None:
    (tmp_path / "page.md").write_text("# Page", encoding="utf-8")
    (tmp_path / "visible.txt").write_text("asset", encoding="utf-8")
    (tmp_path / ".hidden.md").write_text("ignored", encoding="utf-8")
    (tmp_path / "_drafts").mkdir()
    (tmp_path / "_drafts" / "draft.md").write_text("ignored", encoding="utf-8")

    discovery = DocumentDiscovery(tmp_path)
    assert [p.name for p in discovery.documents()] == ["page.md"]
    assert [p.name for p in discovery.static_files()] == ["visible.txt"]


def test_discovery_skips_symlinks_to_files_and_directories(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "page.md").write_text("# Page", encoding="utf-8")
    (source / "static.txt").write_text("asset", encoding="utf-8")

    internal_dir = source / "nested"
    internal_dir.mkdir()
    (internal_dir / "inside.md").write_text("# Nested", encoding="utf-8")

    external_dir = tmp_path / "outside"
    external_dir.mkdir()
    (external_dir / "secret.md").write_text("# Outside", encoding="utf-8")
    (external_dir / "secret.txt").write_text("outside asset", encoding="utf-8")

    _create_symlink(
        source / "internal-alias",
        internal_dir,
        target_is_directory=True,
    )
    _create_symlink(
        source / "external-alias",
        external_dir,
        target_is_directory=True,
    )
    _create_symlink(source / "external-page.md", external_dir / "secret.md")
    _create_symlink(source / "external-asset.txt", external_dir / "secret.txt")
    _create_symlink(source / "broken.txt", tmp_path / "missing.txt")

    discovered = DocumentDiscovery(source).files()

    assert [path.relative_to(source).as_posix() for path in discovered] == [
        "nested/inside.md",
        "page.md",
        "static.txt",
    ]


def test_discovery_does_not_follow_symlink_to_ancestor(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "page.md").write_text("# Page", encoding="utf-8")
    nested = source / "nested"
    nested.mkdir()
    _create_symlink(nested / "back-to-source", source, target_is_directory=True)

    # Isolate discovery so a regression that follows the ancestor link cannot
    # hang the main pytest process indefinitely.
    package_source = Path(__file__).resolve().parents[1] / "src"
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        part for part in (str(package_source), env.get("PYTHONPATH", "")) if part
    )
    script = (
        "from pathlib import Path; import sys; "
        "from docbuild import DocumentDiscovery; "
        "root = Path(sys.argv[1]); "
        "print('\\n'.join(path.relative_to(root).as_posix() "
        "for path in DocumentDiscovery(root).files()))"
    )

    result = subprocess.run(
        [sys.executable, "-c", script, str(source)],
        capture_output=True,
        check=True,
        text=True,
        timeout=5,
        env=env,
    )

    assert result.stdout.splitlines() == ["page.md"]


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



@pytest.mark.parametrize("reverse", [False, True])
def test_detects_file_directory_output_collisions_in_any_order(
    tmp_path: Path, reverse: bool
) -> None:
    document = tmp_path / "guide.md"
    document.write_text("# Guide", encoding="utf-8")
    image = tmp_path / "guide.html" / "image.png"
    image.parent.mkdir()
    image.write_bytes(b"image")

    files = [document, image]
    if reverse:
        files.reverse()

    with pytest.raises(BuildError, match="output collision") as error:
        SiteBuilder(tmp_path)._check_output_collisions(files)

    assert "guide.md" in str(error.value)
    assert "guide.html/image.png" in str(error.value)


def test_build_rejects_file_directory_output_conflicts_before_writing_outputs(
    tmp_path: Path,
) -> None:
    (tmp_path / "guide.md").write_text("# Guide", encoding="utf-8")
    image = tmp_path / "guide.html" / "image.png"
    image.parent.mkdir()
    image.write_bytes(b"image")

    with pytest.raises(BuildError, match="output collision"):
        SiteBuilder(tmp_path).build()

    assert not (tmp_path / "_site").exists()


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


def test_same_size_content_change_with_restored_timestamp_is_rebuilt(tmp_path: Path) -> None:
    _site(tmp_path)
    source = tmp_path / "page.md"
    source.write_text("# First", encoding="utf-8")

    with patch(
        "docbuild.converter.pypandoc.convert_text",
        side_effect=["<h1>First</h1>", "<h1>Other</h1>"],
    ) as convert:
        SiteBuilder(tmp_path).build()
        original_stat = source.stat()

        # Same number of bytes, with the original nanosecond timestamp restored.
        source.write_text("# Other", encoding="utf-8")
        assert source.stat().st_size == original_stat.st_size
        os.utime(source, ns=(original_stat.st_atime_ns, original_stat.st_mtime_ns))
        assert source.stat().st_mtime_ns == original_stat.st_mtime_ns

        SiteBuilder(tmp_path).build()

    assert convert.call_count == 2
    output = (tmp_path / "_site" / "page.html").read_text(encoding="utf-8")
    assert "<h1>Other</h1>" in output


def test_large_static_files_skip_sha256_and_use_metadata_signature(tmp_path: Path) -> None:
    payload = b"binary-media-payload"
    (tmp_path / "large-media.bin").write_bytes(payload)
    config_path = tmp_path / "_config.toml"
    config_path.write_text(
        config_path.read_text(encoding="utf-8") + "content_hash_max_bytes = 4\n",
        encoding="utf-8",
    )

    with patch("docbuild.indexer.hashlib.file_digest") as file_digest:
        SiteBuilder(tmp_path).build()
    file_digest.assert_not_called()

    with FileCache(tmp_path / ".cache.db") as cache:
        record = cache.get("large-media.bin")

    assert record is not None
    signature = record["signature"]
    assert signature["size"] == len(payload)
    assert "sha256" not in signature
    assert {"size", "mtime_ns", "ctime_ns"} == set(signature)


def test_static_files_are_not_recopied_when_unchanged(tmp_path: Path) -> None:
    (tmp_path / "asset.txt").write_text("asset", encoding="utf-8")
    with patch("docbuild.builder.shutil.copy2", wraps=__import__("shutil").copy2) as copy:
        SiteBuilder(tmp_path).build()
        copy.reset_mock()
        SiteBuilder(tmp_path).build()
    copy.assert_not_called()



def test_toolchain_change_rebuilds_documents_but_not_static_assets(
    tmp_path: Path,
) -> None:
    _site(tmp_path)
    (tmp_path / "page.md").write_text("# Body", encoding="utf-8")
    (tmp_path / "asset.txt").write_text("asset", encoding="utf-8")

    with (
        patch("docbuild.converter.pypandoc.convert_text", return_value="<p>Body</p>") as convert,
        patch(
            "docbuild.converter.DocumentConverter.build_signature",
            side_effect=["toolchain-v1", "toolchain-v2"],
        ),
        patch("docbuild.builder.shutil.copy2", wraps=__import__("shutil").copy2) as copy,
    ):
        SiteBuilder(tmp_path).build()
        convert.reset_mock()
        copy.reset_mock()
        SiteBuilder(tmp_path).build()

    # A changed rendering toolchain invalidates HTML, not byte-for-byte copies.
    convert.assert_called_once()
    copy.assert_not_called()


def test_toolchain_fingerprint_covers_parser_and_indexer_modules(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from docbuild.converter import DocumentConverter

    original_read_bytes = Path.read_bytes
    loaded_modules: set[str] = set()

    def track_module_reads(path: Path) -> bytes:
        loaded_modules.add(path.name)
        return original_read_bytes(path)

    distributions: list[str] = []
    monkeypatch.setattr(Path, "read_bytes", track_module_reads)
    monkeypatch.setattr(
        "docbuild.converter.version",
        lambda name: distributions.append(name) or "1.0",
    )
    monkeypatch.setattr(
        "docbuild.converter.pypandoc.get_pandoc_version",
        lambda: "3.8",
    )

    signature = DocumentConverter.build_signature()

    assert signature.startswith("document-toolchain-v1:")
    assert {
        "cache.py",
        "discovery.py",
        "frontmatter.py",
        "indexer.py",
    } <= loaded_modules
    assert {"python-frontmatter", "PyYAML"} <= set(distributions)


def test_toolchain_fingerprint_changes_when_frontmatter_dependency_changes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from docbuild.converter import DocumentConverter

    versions = {
        "Jinja2": "3.1.0",
        "MarkupSafe": "2.1.0",
        "pypandoc": "1.13",
        "python-frontmatter": "1.0",
        "PyYAML": "6.0",
    }
    monkeypatch.setattr(
        "docbuild.converter.version",
        lambda name: versions[name],
    )
    monkeypatch.setattr(
        "docbuild.converter.pypandoc.get_pandoc_version",
        lambda: "3.8",
    )

    original = DocumentConverter.build_signature()
    versions["python-frontmatter"] = "1.1"
    changed = DocumentConverter.build_signature()

    assert changed != original


def test_build_graph_leaf_signature_uses_nul_separators() -> None:
    import hashlib

    graph = BuildGraph()
    graph.add_node("source:page.md", "source", "source-v1")

    digest = hashlib.sha256()
    digest.update(b"source")
    digest.update(b"\0")
    digest.update(b"source:page.md")
    digest.update(b"\0")
    digest.update(b"source-v1")
    digest.update(b"\0")

    assert graph.signature("source:page.md") == f"build-graph-v1:{digest.hexdigest()}"


def test_changed_static_asset_does_not_rebuild_documents(tmp_path: Path) -> None:
    _site(tmp_path)
    (tmp_path / "page.md").write_text("# Body", encoding="utf-8")
    asset = tmp_path / "assets" / "site.css"
    asset.parent.mkdir()
    asset.write_text("body { color: black; }", encoding="utf-8")

    with (
        patch("docbuild.converter.pypandoc.convert_text", return_value="<p>Body</p>") as convert,
        patch("docbuild.builder.shutil.copy2", wraps=__import__("shutil").copy2) as copy,
    ):
        SiteBuilder(tmp_path).build()
        convert.reset_mock()
        copy.reset_mock()

        asset.write_text("body { color: white; }", encoding="utf-8")
        SiteBuilder(tmp_path).build()

    convert.assert_not_called()
    copy.assert_called_once_with(asset, tmp_path / "_site" / "assets" / "site.css")


def test_missing_static_output_is_copied_without_rebuilding_documents(
    tmp_path: Path,
) -> None:
    _site(tmp_path)
    (tmp_path / "page.md").write_text("# Body", encoding="utf-8")
    asset = tmp_path / "assets" / "site.css"
    asset.parent.mkdir()
    asset.write_text("body {}", encoding="utf-8")

    with (
        patch("docbuild.converter.pypandoc.convert_text", return_value="<p>Body</p>") as convert,
        patch("docbuild.builder.shutil.copy2", wraps=__import__("shutil").copy2) as copy,
    ):
        SiteBuilder(tmp_path).build()
        convert.reset_mock()
        copy.reset_mock()
        (tmp_path / "_site" / "assets" / "site.css").unlink()
        SiteBuilder(tmp_path).build()

    convert.assert_not_called()
    copy.assert_called_once_with(asset, tmp_path / "_site" / "assets" / "site.css")


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


def test_unused_template_change_does_not_rebuild_documents(tmp_path: Path) -> None:
    _site(tmp_path)
    (tmp_path / "_templates" / "unused.template").write_text(
        "<aside>Unused</aside>", encoding="utf-8"
    )
    (tmp_path / "page.md").write_text("# Body", encoding="utf-8")

    with patch("docbuild.converter.pypandoc.convert_text", return_value="<h1>Body</h1>") as convert:
        SiteBuilder(tmp_path).build()
        (tmp_path / "_templates" / "unused.template").write_text(
            "<aside>Changed but still unused</aside>", encoding="utf-8"
        )
        SiteBuilder(tmp_path).build()

    assert convert.call_count == 1


def test_template_change_rebuilds_only_documents_using_that_template(tmp_path: Path) -> None:
    _site(tmp_path)
    (tmp_path / "_templates" / "article.template").write_text(
        "<article>{{ page.title }}{{ content }}</article>", encoding="utf-8"
    )
    (tmp_path / "page.md").write_text("# Page", encoding="utf-8")
    (tmp_path / "article.md").write_text(
        "---\ntitle: Article\nlayout: article\n---\n\n# Article",
        encoding="utf-8",
    )

    with patch("docbuild.converter.pypandoc.convert_text", return_value="<p>Body</p>") as convert:
        SiteBuilder(tmp_path).build()
        (tmp_path / "_templates" / "page.template").write_text(
            "<main>Updated {{ content }}</main>", encoding="utf-8"
        )
        SiteBuilder(tmp_path).build()

    # Only page.md uses page.template; article.md uses article.template.
    assert convert.call_count == 3


def test_parent_template_change_rebuilds_only_dependent_documents(tmp_path: Path) -> None:
    _site(
        tmp_path,
        template='{% extends "base.template" %}{% block main %}Page {{ content }}{% endblock %}',
    )
    (tmp_path / "_templates" / "base.template").write_text(
        "{% block main %}Base{% endblock %}", encoding="utf-8"
    )
    (tmp_path / "_templates" / "standalone.template").write_text(
        "<article>{{ content }}</article>", encoding="utf-8"
    )
    (tmp_path / "page.md").write_text("# Page", encoding="utf-8")
    (tmp_path / "standalone.md").write_text(
        "---\nlayout: standalone\n---\n\n# Standalone",
        encoding="utf-8",
    )

    with patch("docbuild.converter.pypandoc.convert_text", return_value="<p>Body</p>") as convert:
        SiteBuilder(tmp_path).build()
        (tmp_path / "_templates" / "base.template").write_text(
            "{% block main %}Changed base{% endblock %}", encoding="utf-8"
        )
        SiteBuilder(tmp_path).build()

    # The page template inherits from base.template; standalone does not.
    assert convert.call_count == 3


def test_dynamic_template_reference_uses_conservative_signature(tmp_path: Path) -> None:
    _site(tmp_path, template='{% include page.partial %}{{ content }}')
    (tmp_path / "_templates" / "first.template").write_text("First", encoding="utf-8")
    (tmp_path / "_templates" / "second.template").write_text("Second", encoding="utf-8")
    (tmp_path / "page.md").write_text(
        "---\npartial: first.template\n---\n\n# Body", encoding="utf-8"
    )

    with patch("docbuild.converter.pypandoc.convert_text", return_value="<p>Body</p>") as convert:
        SiteBuilder(tmp_path).build()
        (tmp_path / "_templates" / "second.template").write_text(
            "Changed second", encoding="utf-8"
        )
        SiteBuilder(tmp_path).build()

    # Dynamic includes cannot be resolved during static analysis, so all
    # templates remain dependencies as a safe fallback.
    assert convert.call_count == 2




def test_reused_builder_refreshes_template_dependency_graph(tmp_path: Path) -> None:
    _site(tmp_path)
    (tmp_path / "page.md").write_text("# Body", encoding="utf-8")
    builder = SiteBuilder(tmp_path)

    with patch("docbuild.converter.pypandoc.convert_text", return_value="<h1>Body</h1>") as convert:
        builder.build()
        (tmp_path / "_templates" / "page.template").write_text(
            "<h1>Changed {{ content }}</h1>", encoding="utf-8"
        )
        builder.build()

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
    assert output.index("Beta|notes/beta.md|/notes/beta.html") < output.index(
        "Alpha|alpha.md|/alpha.html"
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





def test_build_graph_signature_includes_transitive_dependencies() -> None:
    graph = BuildGraph()
    graph.add_node("source:page.md", "document", "source-v1")
    graph.add_node("template:base.template", "template", "base-v1")
    graph.add_node("template:page.template", "template", "page-v1")
    graph.add_node("output:page.html", "output", "render-v1")
    graph.depends_on("template:page.template", "template:base.template")
    graph.depends_on("output:page.html", "source:page.md")
    graph.depends_on("output:page.html", "template:page.template")
    original = graph.signature("output:page.html")

    changed = BuildGraph()
    changed.add_node("source:page.md", "document", "source-v1")
    changed.add_node("template:base.template", "template", "base-v2")
    changed.add_node("template:page.template", "template", "page-v1")
    changed.add_node("output:page.html", "output", "render-v1")
    changed.depends_on("template:page.template", "template:base.template")
    changed.depends_on("output:page.html", "source:page.md")
    changed.depends_on("output:page.html", "template:page.template")

    assert changed.signature("output:page.html") != original


def test_build_graph_detects_cycles() -> None:
    graph = BuildGraph()
    graph.add_node("a", "source", "a")
    graph.add_node("b", "template", "b")
    graph.depends_on("a", "b")
    graph.depends_on("b", "a")

    with pytest.raises(BuildError, match="dependency cycle"):
        graph.signature("a")


def test_build_planner_selects_missing_and_changed_outputs(tmp_path: Path) -> None:
    graph = BuildGraph()
    graph.add_node("source:page.md", "document", "source-v1")
    graph.add_node("output:page.html", "output", "render-v1")
    graph.add_node("output:new.html", "output", "render-v1")
    graph.depends_on("output:page.html", "source:page.md")
    graph.depends_on("output:new.html", "source:page.md")
    signature = graph.signature("output:page.html")

    plan = BuildPlanner().plan(
        graph,
        [
            BuildArtifact(
                node_key="output:page.html",
                destination=tmp_path / "page.html",
                built_signature=signature,
                exists=True,
            ),
            BuildArtifact(
                node_key="output:new.html",
                destination=tmp_path / "new.html",
                built_signature=None,
                exists=False,
            ),
        ],
    )

    assert len(plan.tasks) == 1
    assert plan.tasks[0].reason == "missing output"
    assert len(plan.unchanged) == 1


def test_builder_persists_effective_graph_signatures(tmp_path: Path) -> None:
    _site(tmp_path)
    (tmp_path / "page.md").write_text("# Body", encoding="utf-8")

    with patch("docbuild.converter.pypandoc.convert_text", return_value="<p>Body</p>"):
        SiteBuilder(tmp_path).build()

    with FileCache(tmp_path / ".cache.db") as cache:
        record = cache.get("page.md")
    assert record is not None
    assert record["built_graph_signature"].startswith("build-graph-v1:")


def test_config_change_rebuilds_only_templates_using_that_key(tmp_path: Path) -> None:
    _site(tmp_path, template="{{ site.name }}{{ content }}")
    (tmp_path / "alpha.md").write_text("# Alpha", encoding="utf-8")
    (tmp_path / "beta.md").write_text("# Beta", encoding="utf-8")
    config = tmp_path / "_config.toml"

    with patch("docbuild.converter.pypandoc.convert_text", return_value="<p>Body</p>") as convert:
        SiteBuilder(tmp_path).build()

        # Description is not referenced by the selected template.
        config.write_text(
            config.read_text(encoding="utf-8").replace(
                'description = "Personal website and notes."',
                'description = "Updated description."',
            ),
            encoding="utf-8",
        )
        SiteBuilder(tmp_path).build()
        assert convert.call_count == 2

        # The template does reference site.name, so changing it rebuilds both pages.
        config.write_text(
            config.read_text(encoding="utf-8").replace(
                'name = "Notes"', 'name = "Updated Notes"'
            ),
            encoding="utf-8",
        )
        SiteBuilder(tmp_path).build()

    assert convert.call_count == 4


def test_config_key_dependency_includes_inherited_templates(tmp_path: Path) -> None:
    _site(tmp_path, template='{% extends "base.template" %}{% block main %}{{ content }}{% endblock %}')
    (tmp_path / "_templates" / "base.template").write_text(
        "{{ site.author }}{% block main %}{% endblock %}", encoding="utf-8"
    )
    (tmp_path / "page.md").write_text("# Body", encoding="utf-8")
    config = tmp_path / "_config.toml"

    with patch("docbuild.converter.pypandoc.convert_text", return_value="<p>Body</p>") as convert:
        SiteBuilder(tmp_path).build()
        config.write_text(
            config.read_text(encoding="utf-8").replace(
                'description = "Personal website and notes."',
                'description = "Updated description."',
            ),
            encoding="utf-8",
        )
        SiteBuilder(tmp_path).build()
        assert convert.call_count == 1

        config.write_text(
            config.read_text(encoding="utf-8").replace(
                'author = "Biju Punalor"', 'author = "New Author"'
            ),
            encoding="utf-8",
        )
        SiteBuilder(tmp_path).build()

    assert convert.call_count == 2


def test_site_catalog_change_does_not_rebuild_pages_without_catalog_dependency(
    tmp_path: Path,
) -> None:
    _site(tmp_path, template="<title>{{ page.title }}</title>{{ content }}")
    alpha = tmp_path / "alpha.md"
    beta = tmp_path / "beta.md"
    alpha.write_text("---\ntitle: Alpha\n---\n\nAlpha", encoding="utf-8")
    beta.write_text("---\ntitle: Beta\n---\n\nBeta", encoding="utf-8")

    with patch("docbuild.converter.pypandoc.convert_text", return_value="<p>Body</p>") as convert:
        SiteBuilder(tmp_path).build()
        beta.write_text("---\ntitle: Bravo\n---\n\nBeta", encoding="utf-8")
        SiteBuilder(tmp_path).build()

    # Beta changes; Alpha does not consume site.pages and remains untouched.
    assert convert.call_count == 3


def test_site_catalog_change_rebuilds_only_catalog_consumers(tmp_path: Path) -> None:
    _site(tmp_path, template="<title>{{ page.title }}</title>{{ content }}")
    (tmp_path / "_templates" / "catalog.template").write_text(
        "{% for item in site.pages %}<a>{{ item.title }}</a>{% endfor %}{{ content }}",
        encoding="utf-8",
    )
    alpha = tmp_path / "alpha.md"
    beta = tmp_path / "beta.md"
    catalog = tmp_path / "catalog.md"
    alpha.write_text("---\ntitle: Alpha\n---\n\nAlpha", encoding="utf-8")
    beta.write_text("---\ntitle: Beta\n---\n\nBeta", encoding="utf-8")
    catalog.write_text("---\nlayout: catalog\n---\n\nCatalog", encoding="utf-8")

    with patch("docbuild.converter.pypandoc.convert_text", return_value="<p>Body</p>") as convert:
        SiteBuilder(tmp_path).build()
        beta.write_text("---\ntitle: Bravo\n---\n\nBeta", encoding="utf-8")
        SiteBuilder(tmp_path).build()

    # Beta rebuilds itself; catalog rebuilds because site.pages changed;
    # Alpha does not depend on the virtual catalog node.
    assert convert.call_count == 5
    output = (tmp_path / "_site" / "catalog.html").read_text(encoding="utf-8")
    assert "<a>Bravo</a>" in output


@pytest.mark.parametrize(
    "template",
    [
        '{% for item in site["pages"] %}{{ item.title }}{% endfor %}',
        '{% set context = site %}{% for item in context.pages %}{{ item.title }}{% endfor %}',
    ],
)
def test_site_catalog_dependency_detects_mapping_and_aliased_access(
    tmp_path: Path, template: str
) -> None:
    _site(tmp_path, template=template + "{{ content }}")
    (tmp_path / "alpha.md").write_text("---\ntitle: Alpha\n---\n\nAlpha", encoding="utf-8")
    (tmp_path / "beta.md").write_text("---\ntitle: Beta\n---\n\nBeta", encoding="utf-8")

    with patch("docbuild.converter.pypandoc.convert_text", return_value="<p>Body</p>") as convert:
        SiteBuilder(tmp_path).build()
        (tmp_path / "beta.md").write_text(
            "---\ntitle: Bravo\n---\n\nBeta", encoding="utf-8"
        )
        SiteBuilder(tmp_path).build()

    assert convert.call_count == 4


def test_markdown_conversion_uses_commonmark_with_pipe_tables_and_footnotes(tmp_path: Path) -> None:
    from docbuild.converter import DocumentConverter

    source = tmp_path / "page.md"
    with patch("docbuild.converter.pypandoc.convert_text", return_value="<pre><code></code></pre>") as convert:
        DocumentConverter().convert(source, "```python\nprint('hello')\n```")

    assert convert.call_args.kwargs["format"] == "commonmark+pipe_tables+footnotes"



@pytest.mark.parametrize("url_value", ["notes/python.html", "/notes/python.html"])
def test_page_url_is_site_relative_and_does_not_change_output_path(
    tmp_path: Path, url_value: str
) -> None:
    _site(
        tmp_path,
        template=(
            "<page-url>{{ page.url }}</page-url>"
            "<page-output>{{ page.output }}</page-output>"
            "{% for item in site.pages %}<catalog-url>{{ item.url }}</catalog-url>{% endfor %}"
            "{{ content }}"
        ),
    )
    source = tmp_path / "notes" / "python.md"
    source.parent.mkdir()
    source.write_text(
        f'---\ntitle: Python\nurl: "{url_value}"\n---\n\nPython',
        encoding="utf-8",
    )

    with patch("docbuild.converter.pypandoc.convert_text", return_value="<p>Python</p>"):
        SiteBuilder(tmp_path).build()

    output = (tmp_path / "_site" / "notes" / "python.html").read_text(encoding="utf-8")
    assert "<page-url>/notes/python.html</page-url>" in output
    assert "<page-output>notes/python.html</page-output>" in output
    assert "<catalog-url>/notes/python.html</catalog-url>" in output
    assert (tmp_path / "_site" / "notes" / "python.html").is_file()
    assert not (tmp_path / "_site" / "notes" / "custom.html").exists()


@pytest.mark.parametrize(
    "frontmatter",
    [
        "---\ntitle: Python\n---\n\nPython",
        '---\ntitle: Python\nurl: ""\n---\n\nPython',
    ],
)
def test_missing_or_empty_page_url_defaults_to_output_path(
    tmp_path: Path, frontmatter: str
) -> None:
    _site(tmp_path, template="<page-url>{{ page.url }}</page-url>{{ content }}")
    (tmp_path / "notes").mkdir()
    (tmp_path / "notes" / "python.md").write_text(frontmatter, encoding="utf-8")

    with patch("docbuild.converter.pypandoc.convert_text", return_value="<p>Python</p>"):
        SiteBuilder(tmp_path).build()

    output = (tmp_path / "_site" / "notes" / "python.html").read_text(encoding="utf-8")
    assert "<page-url>/notes/python.html</page-url>" in output


@pytest.mark.parametrize(
    "url_value",
    [
        '"https://example.org/python.html"',
        '"//example.org/python.html"',
        '"notes/../private.html"',
        '"../python.html"',
        '"notes/%2e%2e/private.html"',
        '"notes\\\\python.html"',
        '"notes/python.html?draft=1"',
        '"notes/python.html#section"',
        "12",
        "true",
    ],
)
def test_invalid_page_urls_are_rejected(tmp_path: Path, url_value: str) -> None:
    _site(tmp_path)
    (tmp_path / "page.md").write_text(
        f"---\ntitle: Python\nurl: {url_value}\n---\n\nPython",
        encoding="utf-8",
    )

    with pytest.raises(BuildError, match="frontmatter 'url'"):
        SiteBuilder(tmp_path).build()


def test_page_url_is_used_for_listing_and_canonical_links(tmp_path: Path) -> None:
    _site(
        tmp_path,
        template=(
            '{% extends "base.template" %}'
            "{% block main %}"
            '<a id="current" href="{{ page.url }}">{{ page.title }}</a>'
            "{% for item in site.pages %}"
            '<a id="listing" href="{{ item.url }}">{{ item.title }}</a>'
            "{% endfor %}"
            "{% endblock %}"
        ),
    )
    (tmp_path / "_templates" / "base.template").write_text(
        '<link rel="canonical" href="{{ site.url.rstrip("/") }}{{ page.url }}">'
        "{% block main %}{% endblock %}",
        encoding="utf-8",
    )
    (tmp_path / "notes").mkdir()
    (tmp_path / "notes" / "python.md").write_text(
        "---\ntitle: Python\n---\n\nPython",
        encoding="utf-8",
    )

    with patch("docbuild.converter.pypandoc.convert_text", return_value="<p>Python</p>"):
        SiteBuilder(tmp_path).build()

    output = (tmp_path / "_site" / "notes" / "python.html").read_text(encoding="utf-8")
    assert '<link rel="canonical" href="https://bijumon.github.io/notes/python.html">' in output
    assert '<a id="current" href="/notes/python.html">Python</a>' in output
    assert '<a id="listing" href="/notes/python.html">Python</a>' in output


def test_page_url_change_rebuilds_pages_that_use_the_page_catalog(tmp_path: Path) -> None:
    _site(
        tmp_path,
        template=(
            "{% for item in site.pages %}"
            '<a href="{{ item.url }}">{{ item.title }}</a>'
            "{% endfor %}{{ content }}"
        ),
    )
    alpha = tmp_path / "alpha.md"
    beta = tmp_path / "beta.md"
    alpha.write_text("---\ntitle: Alpha\n---\n\nAlpha", encoding="utf-8")
    beta.write_text(
        '---\ntitle: Beta\nurl: "notes/old.html"\n---\n\nBeta',
        encoding="utf-8",
    )

    with patch("docbuild.converter.pypandoc.convert_text", return_value="<p>Content</p>") as convert:
        SiteBuilder(tmp_path).build()
        beta.write_text(
            '---\ntitle: Beta\nurl: "/notes/new.html"\n---\n\nBeta',
            encoding="utf-8",
        )
        SiteBuilder(tmp_path).build()

    assert convert.call_count == 4
    alpha_output = (tmp_path / "_site" / "alpha.html").read_text(encoding="utf-8")
    beta_output = (tmp_path / "_site" / "beta.html").read_text(encoding="utf-8")
    assert '<a href="/notes/new.html">Beta</a>' in alpha_output
    assert '<a href="/notes/new.html">Beta</a>' in beta_output
    assert (tmp_path / "_site" / "beta.html").is_file()
    assert not (tmp_path / "_site" / "notes" / "new.html").exists()



def test_page_url_percent_encodes_spaces_in_source_and_custom_paths(
    tmp_path: Path,
) -> None:
    _site(tmp_path, template="<page-url>{{ page.url }}</page-url>{{ content }}")
    (tmp_path / "Blender learning path.md").write_text(
        "# Blender", encoding="utf-8"
    )
    custom = tmp_path / "notes" / "Blender learning path.md"
    custom.parent.mkdir()
    custom.write_text(
        '---\ntitle: Blender\nurl: "notes/Blender learning path.html"\n---\n\n'
        "# Blender",
        encoding="utf-8",
    )

    with patch("docbuild.converter.pypandoc.convert_text", return_value="<p>Blender</p>"):
        SiteBuilder(tmp_path).build()

    default_output = (
        tmp_path / "_site" / "Blender learning path.html"
    ).read_text(encoding="utf-8")
    custom_output = (
        tmp_path / "_site" / "notes" / "Blender learning path.html"
    ).read_text(encoding="utf-8")
    assert "<page-url>/Blender%20learning%20path.html</page-url>" in default_output
    assert "<page-url>/notes/Blender%20learning%20path.html</page-url>" in custom_output



def test_timestamp_restore_reapplies_cached_mtime_for_unchanged_source(
    tmp_path: Path,
) -> None:
    _site(tmp_path)
    source = tmp_path / "page.md"
    source.write_text("# Body", encoding="utf-8")

    with patch("docbuild.converter.pypandoc.convert_text", return_value="<h1>Body</h1>") as convert:
        SiteBuilder(tmp_path).build()
        cached_mtime = source.stat().st_mtime_ns
        os.utime(
            source,
            ns=(source.stat().st_atime_ns, cached_mtime + 5_000_000_000),
        )

        summary = restore_source_timestamps(tmp_path, [])
        assert summary.restored == 1
        assert source.stat().st_mtime_ns == cached_mtime

        SiteBuilder(tmp_path).build()

    assert convert.call_count == 1


def test_timestamp_restore_invalidates_changed_paths_even_with_same_size_and_mtime(
    tmp_path: Path,
) -> None:
    _site(tmp_path)
    source = tmp_path / "page.md"
    source.write_text("# First", encoding="utf-8")

    with patch(
        "docbuild.converter.pypandoc.convert_text",
        side_effect=["<h1>First</h1>", "<h1>Other</h1>"],
    ) as convert:
        SiteBuilder(tmp_path).build()
        original_stat = source.stat()
        source.write_text("# Other", encoding="utf-8")
        os.utime(
            source,
            ns=(source.stat().st_atime_ns, original_stat.st_mtime_ns),
        )

        summary = restore_source_timestamps(tmp_path, ["page.md"])
        assert summary.invalidated == 1
        assert source.stat().st_mtime_ns == original_stat.st_mtime_ns

        SiteBuilder(tmp_path).build()

    assert convert.call_count == 2
    assert "<h1>Other</h1>" in (
        tmp_path / "_site" / "page.html"
    ).read_text(encoding="utf-8")


def test_timestamp_restore_rebases_ctime_for_large_files(tmp_path: Path) -> None:
    payload = b"large-media-payload"
    source = tmp_path / "media.bin"
    source.write_bytes(payload)
    config = tmp_path / "_config.toml"
    config.write_text(
        config.read_text(encoding="utf-8") + "content_hash_max_bytes = 4\\n",
        encoding="utf-8",
    )

    with patch("docbuild.builder.shutil.copy2", wraps=__import__("shutil").copy2) as copy:
        SiteBuilder(tmp_path).build()
        original_stat = source.stat()
        os.utime(
            source,
            ns=(original_stat.st_atime_ns, original_stat.st_mtime_ns + 5_000_000_000),
        )

        summary = restore_source_timestamps(tmp_path, [])
        normalized_stat = source.stat()
        assert summary.restored == 1
        assert normalized_stat.st_mtime_ns == original_stat.st_mtime_ns

        with FileCache(tmp_path / ".cache.db") as cache:
            record = cache.get("media.bin")
        assert record is not None
        assert record["signature"]["ctime_ns"] == normalized_stat.st_ctime_ns
        assert record["built_signature"]["ctime_ns"] == normalized_stat.st_ctime_ns

        copy.reset_mock()
        SiteBuilder(tmp_path).build()

    copy.assert_not_called()


def test_timestamp_restore_invalidates_size_mismatches(tmp_path: Path) -> None:
    source = tmp_path / "asset.bin"
    source.write_bytes(b"original")
    SiteBuilder(tmp_path).build()

    source.write_bytes(b"changed-size")
    summary = restore_source_timestamps(tmp_path, [])

    assert summary.invalidated == 1
    with FileCache(tmp_path / ".cache.db") as cache:
        record = cache.get("asset.bin")
    assert record is not None
    assert record["signature"] is None
