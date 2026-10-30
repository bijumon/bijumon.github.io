"""Index source files and decide which outputs need rebuilding."""

import hashlib
import os
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
    signature: dict[str, int | str]
    frontmatter: dict[str, Any]
    body: str | None
    built_signature: dict[str, int | str] | None
    built_template_signature: str | None
    built_site_signature: str | None
    built_graph_signature: str | None = None
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
    def _signature(
        path: Path,
        content_hash_max_bytes: int,
    ) -> dict[str, int | str]:
        """Return a content signature for small files and a metadata signature for large ones.

        Files up to the configured limit are hashed in full. Larger files use
        size, modification time, and change time to avoid reading their contents.
        Change time improves detection when modification time is restored, but
        metadata-only detection cannot guarantee that every content edit is found.
        """
        try:
            stat = path.stat()
            if content_hash_max_bytes <= 0 or stat.st_size > content_hash_max_bytes:
                return {
                    "size": stat.st_size,
                    "mtime_ns": stat.st_mtime_ns,
                    "ctime_ns": stat.st_ctime_ns,
                }

            with path.open("rb") as source:
                # Recheck after opening in case the file changed between stat and open.
                stat = os.fstat(source.fileno())
                if content_hash_max_bytes <= 0 or stat.st_size > content_hash_max_bytes:
                    return {
                        "size": stat.st_size,
                        "mtime_ns": stat.st_mtime_ns,
                        "ctime_ns": stat.st_ctime_ns,
                    }
                digest = hashlib.file_digest(source, "sha256").hexdigest()
        except OSError as exc:
            raise BuildError(f"cannot inspect source file {path}: {exc}") from exc
        return {
            "size": stat.st_size,
            "mtime_ns": stat.st_mtime_ns,
            "sha256": digest,
        }

    def scan(
        self,
        files: Iterable[Path] | None = None,
        *,
        content_hash_max_bytes: int,
    ) -> dict[str, IndexedFile]:
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
            signature = self._signature(path, content_hash_max_bytes)
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
                "built_site_signature": (
                    previous.get("built_site_signature") if previous else None
                ),
                "built_graph_signature": (
                    previous.get("built_graph_signature") if previous else None
                ),
                "deleted": False,
            }
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
                built_site_signature=record["built_site_signature"],
                built_graph_signature=record["built_graph_signature"],
                deleted=False,
            )
        return indexed

    @staticmethod
    def needs_build(
        entry: IndexedFile,
        output: Path,
        template_signature: str,
        site_signature: str,
    ) -> bool:
        """Check source/output state and shared contexts that affect rendering."""
        if not output.is_file() or entry.built_signature != entry.signature:
            return True
        if entry.kind == "document":
            return (
                entry.built_template_signature != template_signature
                or entry.built_site_signature != site_signature
            )
        return False

    def mark_graph_built(self, entry: IndexedFile, graph_signature: str) -> None:
        """Persist the effective build graph signature after writing an output."""
        cache = self._cache()
        record = cache.get(entry.relative_path)
        if record is None:
            raise BuildError(f"missing cache entry after building {entry.relative_path}")
        record["built_signature"] = entry.signature
        record["built_graph_signature"] = graph_signature
        record["built_template_signature"] = None
        record["built_site_signature"] = None
        record["deleted"] = False
        cache.set(entry.relative_path, record)
        entry.built_signature = entry.signature
        entry.built_graph_signature = graph_signature
        entry.built_template_signature = None
        entry.built_site_signature = None

    def mark_built(
        self,
        entry: IndexedFile,
        template_signature: str,
        site_signature: str,
    ) -> None:
        """Record the source/context only after successfully writing its output."""
        cache = self._cache()
        record = cache.get(entry.relative_path)
        if record is None:
            raise BuildError(f"missing cache entry after building {entry.relative_path}")
        record["built_signature"] = entry.signature
        record["built_template_signature"] = (
            template_signature if entry.kind == "document" else None
        )
        record["built_site_signature"] = site_signature if entry.kind == "document" else None
        record["deleted"] = False
        cache.set(entry.relative_path, record)
        entry.built_signature = entry.signature
        entry.built_template_signature = record["built_template_signature"]
        entry.built_site_signature = record["built_site_signature"]
