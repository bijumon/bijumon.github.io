"""Default settings for the static-site builder."""

from typing import Final

SITE_METADATA: Final[dict[str, str]] = {
    "author": "Biju Punalor",
    "name": "Notes",
    "description": "Personal website and notes.",
    "url": "https://bijumon.github.io",
    "language": "en",
    "generator": "docbuild.py",
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
