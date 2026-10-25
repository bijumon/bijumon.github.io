"""Index source files and decide which outputs need rebuilding."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from .cache import FileCache
from .config import DOCUMENT_FORMATS
from .discovery import DocumentDiscovery
from .errors import BuildError
from .frontmatter import FrontmatterReader
from .reporter import Reporter


@dataclass
class IndexedFile:
    """Current source state paired with its last successfully built state."""

    source: Path
    relative_path: str
    kind: str
    signature: dict[str, int]
    frontmatter: dict[str, Any]
    body: str | None
    built_signature: dict[str, int] | None
    built_template_signature: str | None
    deleted: bool = False


class FileIndexer:
    """Compare discovered files with cache records and track successful outputs."""

    def __init__(
        self,
        source: Path,
        discovery: DocumentDiscovery,
        frontmatter: FrontmatterReader,
        reporter: Reporter | None = None,
    ) -> None:
        self.source = source.resolve()
        self.discovery = discovery
        self.frontmatter = frontmatter
        self.reporter = reporter or Reporter()
        self.cache: FileCache | None = None

    def __enter__(self) -> "FileIndexer":
        self.cache = FileCache(self.source / ".cache.db", self.reporter)
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        if self.cache is not None:
            self.cache.close()
            self.cache = None

    def _cache(self) -> FileCache:
        if self.cache is None:
            raise RuntimeError("FileIndexer must be used as a context manager")
        return self.cache

    @staticmethod
    def _signature(path: Path) -> dict[str, int]:
        try:
            stat = path.stat()
        except OSError as exc:
            raise BuildError(f"cannot stat source file {path}: {exc}") from exc
        return {"size": stat.st_size, "mtime_ns": stat.st_mtime_ns}

    def scan(self, files: Iterable[Path] | None = None) -> dict[str, IndexedFile]:
        """Refresh changed source records and mark missing records as deleted.

        A failed build does not advance built_signature; that source is retried
        by a subsequent invocation.
        """
        cache = self._cache()
        source_files = list(files if files is not None else self.discovery.files())
        cached_records = cache.records()
        current_paths = {
            path.relative_to(self.source).as_posix()
            for path in source_files
        }

        for relative_path, record in cached_records.items():
            if relative_path not in current_paths and not record.get("deleted", False):
                record["deleted"] = True
                cache.set(relative_path, record)
                self.reporter.info("Marked deleted: %s (existing output retained)", relative_path)

        indexed: dict[str, IndexedFile] = {}
        for path in sorted(source_files):
            relative_path = path.relative_to(self.source).as_posix()
            kind = "document" if path.suffix.lower() in DOCUMENT_FORMATS else "static"
            signature = self._signature(path)
            previous = cached_records.get(relative_path)
            changed = (
                previous is None
                or previous.get("signature") != signature
                or previous.get("kind") != kind
            )
            reappeared = bool(previous and previous.get("deleted", False))

            metadata: dict[str, Any] = {}
            body: str | None = None
            if kind == "document":
                if changed:
                    metadata, body = self.frontmatter.read(path)
                elif previous is not None:
                    cached_metadata = previous.get("frontmatter", {})
                    metadata = cached_metadata if isinstance(cached_metadata, dict) else {}

            record = {
                "kind": kind,
                "signature": signature,
                "frontmatter": metadata,
                "built_signature": previous.get("built_signature") if previous else None,
                "built_template_signature": (
                    previous.get("built_template_signature") if previous else None
                ),
                "deleted": False,
            }
            # Avoid writing unchanged cache entries on each invocation.
            if changed or previous is None or reappeared:
                cache.set(relative_path, record)

            indexed[relative_path] = IndexedFile(
                source=path,
                relative_path=relative_path,
                kind=kind,
                signature=signature,
                frontmatter=metadata,
                body=body,
                built_signature=record["built_signature"],
                built_template_signature=record["built_template_signature"],
                deleted=False,
            )
        return indexed

    @staticmethod
    def needs_build(
        entry: IndexedFile,
        output: Path,
        template_signature: str,
    ) -> bool:
        """Return whether source, output existence, or document templates require work."""
        if not output.is_file() or entry.built_signature != entry.signature:
            return True
        if entry.kind == "document":
            return entry.built_template_signature != template_signature
        return False

    def mark_built(self, entry: IndexedFile, template_signature: str) -> None:
        """Record the source version only after its output was written successfully."""
        cache = self._cache()
        record = cache.get(entry.relative_path)
        if record is None:
            raise BuildError(f"missing cache entry after building {entry.relative_path}")
        record["built_signature"] = entry.signature
        record["built_template_signature"] = (
            template_signature if entry.kind == "document" else None
        )
        record["deleted"] = False
        cache.set(entry.relative_path, record)
        entry.built_signature = entry.signature
        entry.built_template_signature = record["built_template_signature"]
