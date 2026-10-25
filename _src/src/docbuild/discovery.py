"""Find source documents and static assets."""

from pathlib import Path

from .config import DOCUMENT_FORMATS
from .errors import BuildError


class DocumentDiscovery:
    """Find documents and static files without entering hidden/private paths."""

    def __init__(self, source: Path) -> None:
        self.source = source.resolve()

    @staticmethod
    def _ignored(relative: Path) -> bool:
        return any(part.startswith((".", "_")) for part in relative.parts)

    def files(self) -> list[Path]:
        """Return all visible regular files under the source directory."""
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
        """Return files that use a supported markup extension."""
        return [path for path in self.files() if path.suffix.lower() in DOCUMENT_FORMATS]

    def static_files(self) -> list[Path]:
        """Return files that should be copied without conversion."""
        return [path for path in self.files() if path.suffix.lower() not in DOCUMENT_FORMATS]
