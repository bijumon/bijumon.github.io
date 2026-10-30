"""Convert supported source markup to HTML with Pandoc."""

import hashlib
import json
import platform
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import pypandoc

from .config import DOCUMENT_FORMATS
from .errors import BuildError


class DocumentConverter:
    """Convert source markup to HTML using the installed Pandoc executable."""

    @staticmethod
    def build_signature() -> str:
        """Fingerprint the document-rendering code and its runtime toolchain.

        The signature changes when docbuild's rendering implementation,
        Python, Jinja2, pypandoc, MarkupSafe, or the Pandoc executable changes.
        Static-file copies do not depend on this signature.
        """
        source_digest = hashlib.sha256()
        source_dir = Path(__file__).parent
        output_modules = (
            "builder.py",
            "build_graph.py",
            "config.py",
            "converter.py",
            "renderer.py",
            "template_graph.py",
        )
        try:
            for module_name in output_modules:
                source_digest.update(module_name.encode("utf-8"))
                source_digest.update(b"\0")
                source_digest.update((source_dir / module_name).read_bytes())
                source_digest.update(b"\0")
        except OSError as exc:
            raise BuildError(f"cannot fingerprint docbuild rendering code: {exc}") from exc

        def distribution_version(distribution: str) -> str:
            try:
                return version(distribution)
            except PackageNotFoundError:
                return "unavailable"

        try:
            pandoc_version = str(pypandoc.get_pandoc_version())
        except Exception:
            # The normal conversion path will report a useful error if a
            # document needs Pandoc and the executable is not available.
            pandoc_version = "unavailable"

        runtime = {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "jinja2": distribution_version("Jinja2"),
            "markupsafe": distribution_version("MarkupSafe"),
            "pypandoc": distribution_version("pypandoc"),
            "pandoc": pandoc_version,
        }
        digest = hashlib.sha256()
        digest.update(b"docbuild-document-toolchain-v1\\0")
        digest.update(source_digest.hexdigest().encode("ascii"))
        digest.update(b"\0")
        digest.update(
            json.dumps(runtime, sort_keys=True, separators=(",", ":")).encode("utf-8")
        )
        return f"document-toolchain-v1:{digest.hexdigest()}"

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
