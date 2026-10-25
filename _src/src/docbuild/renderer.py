"""Render converted HTML through Jinja2 templates."""

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, TemplateError, select_autoescape
from markupsafe import Markup

from .config import DEFAULT_LAYOUT, SITE_METADATA
from .errors import BuildError


class TemplateRenderer:
    """Render converted HTML and page metadata through a Jinja2 template."""

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
            return template.render(
                page=metadata,
                site=SITE_METADATA,
                content=Markup(content),
            )
        except TemplateError as exc:
            raise BuildError(f"{source}: cannot render template {name!r}: {exc}") from exc
