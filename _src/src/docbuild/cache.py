"""Persistent file metadata cache backed by Python's dbm.sqlite3."""

import dbm.sqlite3
import json
from datetime import date, datetime, time
from pathlib import Path
from typing import Any

from .errors import BuildError
from .reporter import Reporter


_SCHEMA_KEY = b"__docbuild_schema_version__"
_SCHEMA_VERSION = b"1"
_FILE_PREFIX = b"file:"


def _json_default(value: Any) -> dict[str, str]:
    """Preserve YAML date/time values when serializing frontmatter."""
    if isinstance(value, datetime):
        return {"__docbuild_type__": "datetime", "value": value.isoformat()}
    if isinstance(value, date):
        return {"__docbuild_type__": "date", "value": value.isoformat()}
    if isinstance(value, time):
        return {"__docbuild_type__": "time", "value": value.isoformat()}
    raise TypeError(f"cannot cache a value of type {type(value).__name__}")


def _json_object_hook(value: dict[str, Any]) -> Any:
    """Restore date/time values tagged by _json_default."""
    if set(value) != {"__docbuild_type__", "value"}:
        return value

    value_type = value["__docbuild_type__"]
    constructors = {
        "date": date.fromisoformat,
        "datetime": datetime.fromisoformat,
        "time": time.fromisoformat,
    }
    constructor = constructors.get(value_type)
    if constructor is None:
        return value
    return constructor(value["value"])


class FileCache:
    """Store per-file build records in a SQLite-backed DBM database."""

    def __init__(self, path: Path, reporter: Reporter | None = None) -> None:
        self.path = path
        self.reporter = reporter or Reporter()
        try:
            self._database = dbm.sqlite3.open(str(path), "c")
        except Exception as exc:
            raise BuildError(f"cannot open file cache {path}: {exc}") from exc

        if self._database.get(_SCHEMA_KEY) != _SCHEMA_VERSION:
            for key in list(self._database.keys()):
                if key.startswith(_FILE_PREFIX):
                    del self._database[key]
            self._database[_SCHEMA_KEY] = _SCHEMA_VERSION

    @staticmethod
    def _key(relative_path: str) -> bytes:
        return _FILE_PREFIX + relative_path.encode("utf-8")

    def get(self, relative_path: str) -> dict[str, Any] | None:
        """Return one cached record, or None when it does not exist."""
        payload = self._database.get(self._key(relative_path))
        if payload is None:
            return None
        try:
            record = json.loads(payload.decode("utf-8"), object_hook=_json_object_hook)
        except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError) as exc:
            self.reporter.warning("Ignoring invalid cache record for %s: %s", relative_path, exc)
            del self._database[self._key(relative_path)]
            return None
        if not isinstance(record, dict):
            self.reporter.warning("Ignoring invalid cache record for %s", relative_path)
            del self._database[self._key(relative_path)]
            return None
        return record

    def set(self, relative_path: str, record: dict[str, Any]) -> None:
        """Insert or replace one cache record."""
        try:
            payload = json.dumps(
                record,
                default=_json_default,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")
        except (TypeError, ValueError) as exc:
            raise BuildError(f"cannot serialize cache record for {relative_path}: {exc}") from exc
        self._database[self._key(relative_path)] = payload

    def records(self) -> dict[str, dict[str, Any]]:
        """Return all file records, keyed by source-relative path."""
        result: dict[str, dict[str, Any]] = {}
        for key in list(self._database.keys()):
            if key.startswith(_FILE_PREFIX):
                relative_path = key[len(_FILE_PREFIX):].decode("utf-8")
                record = self.get(relative_path)
                if record is not None:
                    result[relative_path] = record
        return result

    def close(self) -> None:
        """Close the underlying DBM database."""
        self._database.close()

    def __enter__(self) -> "FileCache":
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.close()
