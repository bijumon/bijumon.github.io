"""Orchestrate the incremental static-site build."""

import hashlib
import json
import shutil
from datetime import date, datetime, time
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

from .config import DOCUMENT_FORMATS, OUTPUT_DIR, TEMPLATE_DIR, load_config
from .converter import DocumentConverter
from .discovery import DocumentDiscovery
from .errors import BuildError
from .frontmatter import FrontmatterReader
from .indexer import FileIndexer, IndexedFile
from .renderer import TemplateRenderer
from .reporter import Reporter


class SiteBuilder:
    """Coordinate indexing, conversion, rendering, and output copying."""

    def __init__(self, source: Path, reporter: Reporter | None = None) -> None:
        self.source = source.resolve()
        self.output = self.source / OUTPUT_DIR
        self.template_dir = self.source / TEMPLATE_DIR
        self.reporter = reporter or Reporter()
        self.discovery = DocumentDiscovery(self.source)
        self.frontmatter = FrontmatterReader()
        self.converter = DocumentConverter()
        self.renderer = TemplateRenderer(self.template_dir)
        self.indexer = FileIndexer(
            self.source,
            self.discovery,
            self.frontmatter,
            self.reporter,
        )

    def _output_for(self, source: Path) -> Path:
        relative = source.relative_to(self.source)
        return (self.output / relative).with_suffix(".html")

    @staticmethod
    def _normalize_page_url(value: Any, output_path: str, source: str) -> str:
        """Validate and normalize a page URL as a site-root-relative path.

        Absolute and protocol-relative URLs are deliberately unsupported.
        Query strings, fragments, whitespace, and path traversal are rejected.
        """
        if value is None or value == "":
            value = output_path

        message = f"{source}: frontmatter 'url' must be a site-relative path"
        if not isinstance(value, str):
            raise BuildError(f"{message} (expected a string)")
        if not value or value.isspace():
            raise BuildError(f"{message} (empty or whitespace-only value)")
        if value != value.strip() or any(char.isspace() for char in value):
            raise BuildError(f"{message} (whitespace must be URL-encoded)")
        if any(ord(char) < 0x20 or ord(char) == 0x7F for char in value):
            raise BuildError(f"{message} (control characters are not allowed)")
        if value.startswith("//"):
            raise BuildError(f"{message} (protocol-relative URLs are not supported)")
        if "?" in value or "#" in value:
            raise BuildError(f"{message} (query strings and fragments are not supported)")

        try:
            parsed = urlsplit(value)
        except ValueError as exc:
            raise BuildError(f"{message}: {exc}") from exc
        if parsed.scheme or parsed.netloc:
            raise BuildError(f"{message} (absolute URLs are not supported)")

        path = parsed.path
        decoded_path = unquote(path)
        if "\\" in path or "\\" in decoded_path:
            raise BuildError(f"{message} (backslashes are not allowed)")
        if any(segment == ".." for segment in decoded_path.split("/")):
            raise BuildError(f"{message} (parent-directory segments are not allowed)")
        if not path:
            raise BuildError(f"{message} (path is empty)")

        return path if path.startswith("/") else f"/{path}"

    def _page_metadata(self, relative_path: str, entry: IndexedFile) -> dict[str, Any]:
        """Build the canonical metadata dictionary used for both page and site rendering."""
        output_path = Path(relative_path).with_suffix(".html").as_posix()
        page = dict(entry.frontmatter)
        page["source"] = relative_path
        page["output"] = output_path
        page["url"] = self._normalize_page_url(
            page.get("url"),
            output_path,
            relative_path,
        )
        return page

    def _template_signature(self) -> str:
        """Hash all template paths and contents, including nested templates."""
        digest = hashlib.sha256()
        if not self.template_dir.is_dir():
            digest.update(b"missing-template-directory")
            return digest.hexdigest()

        try:
            templates = sorted(
                path for path in self.template_dir.rglob("*") if path.is_file()
            )
            for template in templates:
                relative = template.relative_to(self.template_dir).as_posix()
                digest.update(relative.encode("utf-8"))
                digest.update(b"\0")
                digest.update(template.read_bytes())
                digest.update(b"\0")
        except OSError as exc:
            raise BuildError(f"cannot read templates in {self.template_dir}: {exc}") from exc
        return digest.hexdigest()

    def _check_output_collisions(self, files: list[Path]) -> None:
        """Reject duplicate destinations and file/directory prefix conflicts."""
        destinations: dict[Path, Path] = {}
        for source in files:
            if source.suffix.lower() in DOCUMENT_FORMATS:
                destination = self._output_for(source)
            else:
                destination = self.output / source.relative_to(self.source)

            previous = destinations.get(destination)
            if previous is not None:
                raise BuildError(
                    f"output collision: {previous.relative_to(self.source)} and "
                    f"{source.relative_to(self.source)} both map to "
                    f"{destination.relative_to(self.output)}"
                )
            destinations[destination] = source

        # Check after collecting all destinations so the result does not depend
        # on discovery order (a descendant may be encountered before its file
        # ancestor, or vice versa).
        for destination, source in destinations.items():
            parent = destination.parent
            while parent != self.output:
                previous = destinations.get(parent)
                if previous is not None:
                    raise BuildError(
                        f"output collision: {previous.relative_to(self.source)} maps to "
                        f"{parent.relative_to(self.output)} as a file, but "
                        f"{source.relative_to(self.source)} requires it to be a "
                        f"directory for {destination.relative_to(self.output)}"
                    )
                parent = parent.parent

    @staticmethod
    def _json_default(value: Any) -> str:
        """Serialize frontmatter date/time values consistently for signatures."""
        if isinstance(value, (datetime, date, time)):
            return f"{type(value).__name__}:{value.isoformat()}"
        raise TypeError(f"cannot serialize {type(value).__name__} in site page metadata")

    @classmethod
    def _site_signature(cls, site: dict[str, Any]) -> str:
        """Hash shared site context so pages rebuild when site.pages changes."""
        try:
            payload = json.dumps(
                site,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
                default=cls._json_default,
            ).encode("utf-8")
        except (TypeError, ValueError) as exc:
            raise BuildError(f"cannot serialize site page metadata: {exc}") from exc
        return hashlib.sha256(payload).hexdigest()

    def _site_context(
        self,
        indexed: dict[str, IndexedFile],
        site_metadata: dict[str, Any],
    ) -> dict[str, Any]:
        """Build deterministic site metadata and a list of every source page."""
        pages = [
            self._page_metadata(relative_path, entry)
            for relative_path, entry in sorted(indexed.items())
            if entry.kind == "document"
        ]
        return {**site_metadata, "pages": pages}

    def build(self) -> None:
        """Incrementally build changed documents and copy changed static files."""
        config = load_config(self.source)
        content_hash_max_bytes = config["content_hash_max_bytes"]
        # Hash policy is an internal build setting, not public template metadata.
        site_metadata = {
            key: value
            for key, value in config.items()
            if key != "content_hash_max_bytes"
        }
        files = self.discovery.files()
        self._check_output_collisions(files)
        template_signature = self._template_signature()

        with self.indexer as indexer:
            indexed = indexer.scan(
                files,
                content_hash_max_bytes=content_hash_max_bytes,
            )
            site = self._site_context(indexed, site_metadata)
            page_metadata = {
                page["source"]: page
                for page in site["pages"]
            }
            site_signature = self._site_signature(site)
            self.output.mkdir(parents=True, exist_ok=True)

            for source in files:
                relative = source.relative_to(self.source).as_posix()
                entry = indexed[relative]
                if entry.kind != "document":
                    continue

                destination = self._output_for(source)
                if not indexer.needs_build(
                    entry, destination, template_signature, site_signature
                ):
                    self.reporter.info("Unchanged: %s", relative)
                    continue

                if entry.body is None:
                    _, body = self.frontmatter.read(source)
                else:
                    body = entry.body

                # Use the same normalized metadata object that appears in site.pages.
                metadata = page_metadata[relative]
                html = self.converter.convert(source, body)
                rendered = self.renderer.render(source, metadata, html, site=site)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(rendered, encoding="utf-8")
                indexer.mark_built(entry, template_signature, site_signature)
                self.reporter.info(
                    "Built %s -> %s",
                    relative,
                    destination.relative_to(self.output).as_posix(),
                )

            for source in files:
                relative = source.relative_to(self.source).as_posix()
                entry = indexed[relative]
                if entry.kind == "document":
                    continue

                destination = self.output / source.relative_to(self.source)
                if not indexer.needs_build(
                    entry, destination, template_signature, site_signature
                ):
                    self.reporter.info("Unchanged: %s", relative)
                    continue

                destination.parent.mkdir(parents=True, exist_ok=True)
                try:
                    shutil.copy2(source, destination)
                except OSError as exc:
                    raise BuildError(f"cannot copy {source} to {destination}: {exc}") from exc
                indexer.mark_built(entry, template_signature, site_signature)
                self.reporter.info("Copied %s", relative)
