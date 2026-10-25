"""Orchestrate the incremental static-site build."""

import hashlib
import shutil
from pathlib import Path

from .config import DOCUMENT_FORMATS, OUTPUT_DIR, TEMPLATE_DIR
from .converter import DocumentConverter
from .discovery import DocumentDiscovery
from .errors import BuildError
from .frontmatter import FrontmatterReader
from .indexer import FileIndexer
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

    def build(self) -> None:
        """Incrementally build changed documents and copy changed static files."""
        files = self.discovery.files()
        self._check_output_collisions(files)
        template_signature = self._template_signature()

        with self.indexer as indexer:
            indexed = indexer.scan(files)
            self.output.mkdir(parents=True, exist_ok=True)

            for source in files:
                relative = source.relative_to(self.source).as_posix()
                entry = indexed[relative]
                if entry.kind != "document":
                    continue

                destination = self._output_for(source)
                if not indexer.needs_build(entry, destination, template_signature):
                    self.reporter.info("Unchanged: %s", relative)
                    continue

                if entry.body is None:
                    metadata, body = self.frontmatter.read(source)
                else:
                    metadata, body = entry.frontmatter, entry.body

                html = self.converter.convert(source, body)
                rendered = self.renderer.render(source, metadata, html)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(rendered, encoding="utf-8")
                indexer.mark_built(entry, template_signature)
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
                if not indexer.needs_build(entry, destination, template_signature):
                    self.reporter.info("Unchanged: %s", relative)
                    continue

                destination.parent.mkdir(parents=True, exist_ok=True)
                try:
                    shutil.copy2(source, destination)
                except OSError as exc:
                    raise BuildError(f"cannot copy {source} to {destination}: {exc}") from exc
                indexer.mark_built(entry, template_signature)
                self.reporter.info("Copied %s", relative)
