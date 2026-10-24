#!/usr/bin/env python3
"""Build Markdown and Djot documents into a small static site."""

import argparse
import shutil
import sys
from pathlib import Path
from typing import Any

import frontmatter
from frontmatter.default_handlers import TOMLHandler
import pypandoc
from jinja2 import Environment, FileSystemLoader, TemplateError, select_autoescape
from markupsafe import Markup

# Edit these values to configure the site's global metadata.
site = {
    "name": "Biju Punalor",
    "description": "Personal website and notes.",
    "url": "https://bijumon.github.io",
}

DOCUMENT_FORMATS = {
    ".md": "markdown",
    ".markdown": "markdown",
    ".dj": "djot",
    ".djot": "djot",
}
DEFAULT_LAYOUT = "page.template"
OUTPUT_DIR = "_site"
TEMPLATE_DIR = "_templates"


class BuildError(Exception):
    """An actionable error that should stop the build."""


class DocumentDiscovery:
    """Find documents and static files without entering hidden/private paths."""

    def __init__(self, source: Path) -> None:
        self.source = source.resolve()

    @staticmethod
    def _ignored(relative: Path) -> bool:
        return any(part.startswith((".", "_")) for part in relative.parts)

    def files(self) -> list[Path]:
        found: list[Path] = []
        pending = [self.source]
        while pending:
            directory = pending.pop()
            try:
                children = sorted(directory.iterdir(), reverse=True)
            except OSError as exc:
                raise BuildError(f"cannot read directory {directory}: {exc}") from exc
            for path in children:
                relative = path.relative_to(self.source)
                if self._ignored(relative):
                    continue
                if path.is_dir():
                    pending.append(path)
                elif path.is_file():
                    found.append(path)
        return sorted(found)

    def documents(self) -> list[Path]:
        return [path for path in self.files() if path.suffix.lower() in DOCUMENT_FORMATS]

    def static_files(self) -> list[Path]:
        return [path for path in self.files() if path.suffix.lower() not in DOCUMENT_FORMATS]


class FrontmatterReader:
    """Read YAML (`---`) and TOML (`+++`) frontmatter."""

    def read(self, path: Path) -> tuple[dict[str, Any], str]:
        try:
            text = path.read_text(encoding="utf-8")
            first_line = text.splitlines()[0].strip() if text.splitlines() else ""
            if first_line in {"+++", "---"}:
                delimiter = first_line
                if delimiter not in text.splitlines()[1:]:
                    raise BuildError(f"{path}: missing closing {delimiter!r} frontmatter delimiter")
            if first_line == "+++":
                handler = TOMLHandler()
                post = frontmatter.loads(text, handler=handler)
            elif first_line == "---":
                post = frontmatter.loads(text)
            else:
                return {}, text
        except BuildError:
            raise
        except Exception as exc:
            raise BuildError(f"{path}: cannot parse frontmatter: {exc}") from exc

        metadata = post.metadata
        if not isinstance(metadata, dict):
            raise BuildError(f"{path}: frontmatter must be a mapping of keys to values")
        return metadata, post.content


class DocumentConverter:
    """Convert source markup to HTML using the installed Pandoc executable."""

    def convert(self, source: Path, text: str) -> str:
        source_format = DOCUMENT_FORMATS[source.suffix.lower()]
        try:
            return pypandoc.convert_text(
                text,
                to="html5",
                format=source_format,
                extra_args=["--wrap=none"],
            )
        except Exception as exc:
            raise BuildError(f"{source}: document conversion failed: {exc}") from exc


class TemplateRenderer:
    """Render converted HTML and metadata through a Jinja2 template."""

    def __init__(self, template_dir: Path) -> None:
        self.environment = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(default=True),
        )

    @staticmethod
    def _template_name(layout: Any, source: Path) -> str:
        if layout is None or layout == "":
            return DEFAULT_LAYOUT
        if not isinstance(layout, str):
            raise BuildError(f"{source}: frontmatter 'layout' must be a string")
        name = layout if layout.endswith(".template") else f"{layout}.template"
        candidate = Path(name)
        if candidate.is_absolute() or ".." in candidate.parts:
            raise BuildError(f"{source}: invalid layout name {layout!r}")
        return name

    def render(self, source: Path, metadata: dict[str, Any], content: str) -> str:
        name = self._template_name(metadata.get("layout"), source)
        try:
            template = self.environment.get_template(name)
            return template.render(page=metadata, site=site, content=Markup(content))
        except TemplateError as exc:
            raise BuildError(f"{source}: cannot render template {name!r}: {exc}") from exc


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
        files = self.discovery.files()
        documents = [p for p in files if p.suffix.lower() in DOCUMENT_FORMATS]
        static_files = [p for p in files if p.suffix.lower() not in DOCUMENT_FORMATS]

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
            print(f"Built {source.relative_to(self.source)} -> {destination.relative_to(self.output)}")

        for source in static_files:
            relative = source.relative_to(self.source)
            destination = self.output / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            print(f"Copied {relative}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Markdown and Djot files into _site/")
    parser.add_argument(
        "source_dir",
        nargs="?",
        default=".",
        help="source directory (default: current working directory)",
    )
    args = parser.parse_args(argv)
    source = Path(args.source_dir).resolve()
    if not source.is_dir():
        print(f"error: source directory does not exist: {source}", file=sys.stderr)
        return 2

    try:
        SiteBuilder(source).build()
    except (BuildError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
