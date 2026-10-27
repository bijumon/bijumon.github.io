"""Static-site settings and site metadata loading."""

import tomllib
from pathlib import Path
from typing import Any, Final

from .errors import BuildError

SITE_CONFIG_FILE: Final[str] = "_config.toml"
REQUIRED_SITE_METADATA: Final[tuple[str, ...]] = ("name", "description", "url")

DOCUMENT_FORMATS: Final[dict[str, str]] = {
    ".md": "commonmark+pipe_tables+footnotes",
    ".markdown": "commonmark+pipe_tables+footnotes",
    ".dj": "djot",
    ".djot": "djot",
}

DEFAULT_LAYOUT: Final[str] = "page.template"
OUTPUT_DIR: Final[str] = "_site"
TEMPLATE_DIR: Final[str] = "_templates"


def load_site_metadata(source: Path) -> dict[str, Any]:
    """Load site metadata from the source root's required TOML config."""
    path = source / SITE_CONFIG_FILE
    try:
        with path.open("rb") as config_file:
            metadata = tomllib.load(config_file)
    except FileNotFoundError as exc:
        raise BuildError(f"required site configuration file not found: {path}") from exc
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise BuildError(f"cannot load site configuration {path}: {exc}") from exc

    missing = [
        key
        for key in REQUIRED_SITE_METADATA
        if not isinstance(metadata.get(key), str) or not metadata[key].strip()
    ]
    if missing:
        fields = ", ".join(missing)
        raise BuildError(
            f"{path}: required metadata fields must be non-empty strings: {fields}"
        )

    return metadata
