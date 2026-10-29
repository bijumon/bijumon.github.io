"""Default settings and TOML configuration loading for the static-site builder."""

import tomllib
from pathlib import Path
from typing import Any, Final

from .errors import BuildError


CONFIG_DEFAULTS: Final[dict[str, Any]] = {
    "author": "Unknown Author",
    "name": "Untitled Site",
    "description": "A website built with docbuild.",
    "url": "https://example.com",
    "language": "en",
    "generator": "docbuild",
    "version": "0.5.0",
    # Files above this size use metadata-based detection instead of full hashing.
    # Set to 0 to disable full-content hashing for all files.
    "content_hash_max_bytes": 100 * 1024 * 1024,
}

DOCUMENT_FORMATS: Final[dict[str, str]] = {
    ".md": "commonmark+pipe_tables+footnotes",
    ".markdown": "commonmark+pipe_tables+footnotes",
    ".dj": "djot",
    ".djot": "djot",
}

DEFAULT_LAYOUT: Final[str] = "page.template"
OUTPUT_DIR: Final[str] = "_site"
TEMPLATE_DIR: Final[str] = "_templates"


def load_config(source: Path) -> dict[str, Any]:
    """Load root-level site settings, falling back to application defaults.

    The configuration file is required even when all values could be supplied
    by defaults. Site-specific values in TOML override matching defaults.
    """
    config_path = source / "_config.toml"
    try:
        with config_path.open("rb") as stream:
            settings = tomllib.load(stream)
    except FileNotFoundError as exc:
        raise BuildError(
            f"required configuration file not found: {config_path}"
        ) from exc
    except tomllib.TOMLDecodeError as exc:
        raise BuildError(
            f"invalid TOML in configuration file {config_path}: {exc}"
        ) from exc
    except (OSError, UnicodeDecodeError) as exc:
        raise BuildError(
            f"cannot read configuration file {config_path}: {exc}"
        ) from exc

    config = {**CONFIG_DEFAULTS, **settings}
    hash_limit = config["content_hash_max_bytes"]
    if (
        isinstance(hash_limit, bool)
        or not isinstance(hash_limit, int)
        or hash_limit < 0
    ):
        raise BuildError(
            "content_hash_max_bytes must be a non-negative integer "
            f"in {config_path}"
        )

    return config
