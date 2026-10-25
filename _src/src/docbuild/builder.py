"""Orchestrate the static-site build."""

import shutil
from pathlib import Path

from .config import DOCUMENT_FORMATS, OUTPUT_DIR, TEMPLATE_DIR
from .converter import DocumentConverter
from .discovery import DocumentDiscovery
from .errors import BuildError
from .frontmatter import FrontmatterReader
from .renderer import TemplateRenderer


class SiteBuilder:
    """Coordinate discovery, conversion, rendering, and output copying."""

    def __init__(self, source: Path) -> None:
        self.source = source.resolve()
        self.output = self.source / OUTPUT_DIR
        self.discovery = DocumentDiscovery(self.source)
        self.frontmatter = FrontmatterReader()
        self.converter = DocumentConverter()
        self.renderer = TemplateRenderer(self.source / TEMPLATE_DIR)

    def _output_for(self, source: Path) -> Path:
        relative = source.relative_to(self.source)
        return (self.output / relative).with_suffix(".html")

    def build(self) -> None:
        """Build markup documents and copy visible static files to the output."""
        files = self.discovery.files()
        documents = [path for path in files if path.suffix.lower() in DOCUMENT_FORMATS]
        static_files = [path for path in files if path.suffix.lower() not in DOCUMENT_FORMATS]

        # Detect ambiguous output paths before writing any generated content.
        destinations: dict[Path, Path] = {}
        for source in documents:
            destination = self._output_for(source)
            previous = destinations.get(destination)
            if previous is not None:
                raise BuildError(
                    f"output collision: {previous.relative_to(self.source)} and "
                    f"{source.relative_to(self.source)} both map to "
                    f"{destination.relative_to(self.output)}"
                )
            destinations[destination] = source

        self.output.mkdir(parents=True, exist_ok=True)
        for source in documents:
            metadata, body = self.frontmatter.read(source)
            html = self.converter.convert(source, body)
            rendered = self.renderer.render(source, metadata, html)
            destination = self._output_for(source)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(rendered, encoding="utf-8")
            print(
                f"Built {source.relative_to(self.source)} -> "
                f"{destination.relative_to(self.output)}"
            )

        for source in static_files:
            relative = source.relative_to(self.source)
            destination = self.output / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            print(f"Copied {relative}")
