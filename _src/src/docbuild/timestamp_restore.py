"""Normalize checked-out source timestamps against the persistent build cache."""

import argparse
import os
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable

from .cache import FileCache
from .errors import BuildError
from .reporter import Reporter


@dataclass(frozen=True)
class TimestampRestoreSummary:
    """Counts of cache records handled during timestamp normalization."""

    restored: int = 0
    invalidated: int = 0
    skipped: int = 0


def _relative_source_path(value: str) -> str | None:
    """Accept only normalized, source-relative POSIX paths."""
    if not value or "\x00" in value:
        return None
    path = PurePosixPath(value)
    if path.is_absolute() or any(part == ".." for part in path.parts):
        return None
    normalized = path.as_posix()
    return normalized if normalized not in ("", ".") else None


def restore_source_timestamps(
    source: Path,
    changed_paths: Iterable[str],
    reporter: Reporter | None = None,
) -> TimestampRestoreSummary:
    """Restore cached mtimes for unchanged files and invalidate changed records.

    The caller supplies paths changed between the commit represented by the
    restored cache and the checked-out commit. Unchanged files have their
    cached mtime restored. For metadata-only signatures, ctime cannot be
    restored, so both current and successfully-built signatures are rebased
    to the current ctime after the source mtime is normalized.
    """
    root = source.resolve()
    reporter = reporter or Reporter()
    cache_path = root / ".cache.db"
    if not cache_path.is_file():
        reporter.warning("Skipping timestamp restoration: cache not found at %s", cache_path)
        return TimestampRestoreSummary()

    changed = {
        normalized
        for value in changed_paths
        if (normalized := _relative_source_path(value)) is not None
    }

    restored = 0
    invalidated = 0
    skipped = 0

    try:
        with FileCache(cache_path, reporter) as cache:
            for relative_path, record in cache.records().items():
                if record.get("deleted", False):
                    skipped += 1
                    continue

                normalized = _relative_source_path(relative_path)
                if normalized is None or normalized != relative_path:
                    skipped += 1
                    continue

                if relative_path in changed:
                    # Force a rebuild even if metadata happens to match the old
                    # signature (for example, a same-size edit with preserved mtime).
                    record["signature"] = None
                    cache.set(relative_path, record)
                    invalidated += 1
                    continue

                candidate = root.joinpath(*PurePosixPath(relative_path).parts)
                try:
                    resolved = candidate.resolve(strict=True)
                    if not resolved.is_relative_to(root) or not candidate.is_file():
                        skipped += 1
                        continue
                    stat = candidate.stat()
                except OSError:
                    # Missing files are handled by the normal index scan.
                    skipped += 1
                    continue

                signature = record.get("signature")
                if not isinstance(signature, dict):
                    skipped += 1
                    continue

                cached_size = signature.get("size")
                cached_mtime = signature.get("mtime_ns")
                if (
                    not isinstance(cached_size, int)
                    or isinstance(cached_size, bool)
                    or not isinstance(cached_mtime, int)
                    or isinstance(cached_mtime, bool)
                ):
                    record["signature"] = None
                    cache.set(relative_path, record)
                    invalidated += 1
                    continue

                if stat.st_size != cached_size:
                    # The Git path comparison and the cached record disagree;
                    # prefer a rebuild over normalizing a potentially changed file.
                    record["signature"] = None
                    cache.set(relative_path, record)
                    invalidated += 1
                    continue

                try:
                    if stat.st_mtime_ns != cached_mtime:
                        os.utime(
                            candidate,
                            ns=(stat.st_atime_ns, cached_mtime),
                        )
                    normalized_stat = candidate.stat()
                except OSError:
                    record["signature"] = None
                    cache.set(relative_path, record)
                    invalidated += 1
                    continue

                if normalized_stat.st_mtime_ns != cached_mtime:
                    # Some filesystems cannot represent the cached nanosecond
                    # value exactly. Do not claim that normalization succeeded.
                    record["signature"] = None
                    cache.set(relative_path, record)
                    invalidated += 1
                    continue

                signature = dict(signature)
                signature["mtime_ns"] = normalized_stat.st_mtime_ns
                if "ctime_ns" in signature:
                    signature["ctime_ns"] = normalized_stat.st_ctime_ns
                record["signature"] = signature

                built_signature = record.get("built_signature")
                if isinstance(built_signature, dict):
                    built_signature = dict(built_signature)
                    if "mtime_ns" in built_signature:
                        built_signature["mtime_ns"] = normalized_stat.st_mtime_ns
                    if "ctime_ns" in built_signature:
                        built_signature["ctime_ns"] = normalized_stat.st_ctime_ns
                    record["built_signature"] = built_signature

                cache.set(relative_path, record)
                restored += 1
    except BuildError:
        raise

    summary = TimestampRestoreSummary(
        restored=restored,
        invalidated=invalidated,
        skipped=skipped,
    )
    reporter.info(
        "Restored source timestamps: %d unchanged, invalidated %d, skipped %d",
        summary.restored,
        summary.invalidated,
        summary.skipped,
    )
    return summary


def main(argv: list[str] | None = None) -> int:
    """Restore cached source mtimes before an incremental build."""
    parser = argparse.ArgumentParser(
        description="Restore cached mtimes for source files unchanged since a cached build."
    )
    parser.add_argument(
        "source_dir",
        nargs="?",
        default=".",
        help="site source directory (default: current working directory)",
    )
    parser.add_argument(
        "--changed-files",
        required=True,
        type=Path,
        help="NUL-delimited file containing paths changed since the cached build",
    )
    args = parser.parse_args(argv)

    try:
        changed_paths = (
            os.fsdecode(value)
            for value in args.changed_files.read_bytes().split(b"\x00")
            if value
        )
        restore_source_timestamps(
            Path(args.source_dir),
            changed_paths,
            Reporter(),
        )
    except (BuildError, OSError) as exc:
        Reporter().error("%s", exc)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
