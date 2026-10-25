"""Convert supported source markup to HTML with Pandoc."""

from pathlib import Path

import pypandoc

from .config import DOCUMENT_FORMATS
from .errors import BuildError


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
