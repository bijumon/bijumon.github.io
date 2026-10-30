"""Run an incremental development server with safe source watching.

The source watcher is deliberately independent of LiveReload's recursive
watcher: the latter follows directory symlinks. LiveReload watches only a
temporary signal file, which is touched after a successful build changes
generated output.
"""

from __future__ import annotations

import argparse
import os
import stat
import tempfile
import threading
import time
from pathlib import Path
from typing import Any, Callable

from .builder import SiteBuilder
from .reporter import Reporter


_DEFAULT_HOST = "0.0.0.0"
_DEFAULT_PORT = 8000
_DEFAULT_LIVEPORT = 35729
_DEFAULT_POLL_INTERVAL = 0.4
_DEFAULT_DEBOUNCE = 0.35

_IGNORED_DIRECTORIES = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        ".cvs",
        ".venv",
        ".tox",
        ".nox",
        ".cache",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".uv_cache",
        "__pycache__",
        "__pypackages__",
        "venv",
        "env",
        "node_modules",
        "bower_components",
        "site-packages",
        "_site",
    }
)
_IGNORED_SUFFIXES = frozenset(
    {".pyc", ".pyo", ".swp", ".swo", ".tmp", ".bak", ".orig", ".rej"}
)


def _is_temporary_name(name: str) -> bool:
    """Return whether a filename is a common editor or interpreter by-product."""
    return (
        name.startswith(".#")
        or name.endswith("~")
        or Path(name).suffix.lower() in _IGNORED_SUFFIXES
    )


def _is_watchable_file(relative: Path) -> bool:
    """Apply docbuild discovery rules plus explicit config/template exceptions."""
    if relative == Path("_config.toml"):
        return True

    if not relative.parts or any(part in _IGNORED_DIRECTORIES for part in relative.parts):
        return False
    if _is_temporary_name(relative.name):
        return False

    if relative.parts[0] == "_templates":
        # Templates are normally private paths, but are explicit build inputs.
        return True

    # Match DocumentDiscovery._ignored() for ordinary source and asset paths.
    return not any(part.startswith((".", "_")) for part in relative.parts)


def _should_descend(relative: Path) -> bool:
    """Decide whether a source directory may be visited by the polling watcher."""
    if any(part in _IGNORED_DIRECTORIES for part in relative.parts):
        return False
    if relative.parts and relative.parts[0] == "_templates":
        return True
    return not any(part.startswith((".", "_")) for part in relative.parts)


def _file_snapshot(root: Path, *, source_inputs: bool) -> dict[str, tuple[int, int, int]]:
    """Return a cheap, symlink-safe snapshot of regular files below root.

    Size, mtime, and ctime detect ordinary edits, replacements, creations, and
    deletions without hashing large binary assets. The builder's own indexer
    remains authoritative and computes its configured content signatures.
    """
    result: dict[str, tuple[int, int, int]] = {}

    def raise_walk_error(error: OSError) -> None:
        raise error

    for current, directories, filenames in os.walk(
        root,
        topdown=True,
        followlinks=False,
        onerror=raise_walk_error,
    ):
        current_path = Path(current)
        relative_root = current_path.relative_to(root)

        directories[:] = [
            name
            for name in sorted(directories)
            if not (current_path / name).is_symlink()
            and _should_descend(relative_root / name)
        ]

        for filename in filenames:
            path = current_path / filename
            if path.is_symlink():
                continue

            relative = path.relative_to(root)
            if source_inputs and not _is_watchable_file(relative):
                continue
            if not source_inputs and _is_temporary_name(filename):
                continue

            try:
                info = path.stat(follow_symlinks=False)
            except OSError:
                # A file may disappear between os.walk and stat; the next poll
                # will observe the resulting stable snapshot.
                continue
            if not stat.S_ISREG(info.st_mode):
                continue

            result[relative.as_posix()] = (
                info.st_size,
                info.st_mtime_ns,
                info.st_ctime_ns,
            )

    return result


class SourceWatcher:
    """Poll build inputs safely and coalesce bursts of filesystem changes."""

    def __init__(
        self,
        source: Path,
        callback: Callable[[], Any],
        reporter: Reporter | None = None,
        *,
        poll_interval: float = _DEFAULT_POLL_INTERVAL,
        debounce: float = _DEFAULT_DEBOUNCE,
    ) -> None:
        if poll_interval <= 0:
            raise ValueError("poll_interval must be greater than zero")
        if debounce < 0:
            raise ValueError("debounce cannot be negative")

        self.source = source.resolve()
        self.callback = callback
        self.reporter = reporter or Reporter()
        self.poll_interval = poll_interval
        self.debounce = debounce

        # Establish the baseline before the initial build. Changes made while
        # that build is running are therefore still noticed by the first poll.
        self._snapshot = self.snapshot()
        self._pending_since: float | None = None
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def snapshot(self) -> dict[str, tuple[int, int, int]]:
        """Return the current source-input snapshot."""
        return _file_snapshot(self.source, source_inputs=True)

    def poll_once(self, *, now: float | None = None) -> bool:
        """Poll once; return True when a coalesced change invokes the callback.

        The injectable monotonic timestamp keeps debounce behavior deterministic
        in tests without sleeping or starting a background thread.
        """
        current_time = time.monotonic() if now is None else now
        current = self.snapshot()

        if current != self._snapshot:
            self._snapshot = current
            self._pending_since = current_time
            return False

        if (
            self._pending_since is not None
            and current_time - self._pending_since >= self.debounce
        ):
            self._pending_since = None
            try:
                self.callback()
            except Exception as exc:  # Keep the development watcher alive.
                self.reporter.error("Development rebuild callback failed: %s", exc)
            return True

        return False

    def _run(self) -> None:
        while not self._stop_event.wait(self.poll_interval):
            try:
                self.poll_once()
            except OSError as exc:
                self.reporter.warning("Cannot scan source inputs: %s", exc)

    def start(self) -> None:
        """Start the polling thread."""
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run,
            name="docbuild-source-watcher",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        """Stop polling and wait for any in-progress callback to finish."""
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join()
            self._thread = None


def _create_livereload_server() -> Any:
    """Import LiveReload lazily so normal builds do not require it."""
    try:
        from livereload import Server
    except ImportError as exc:
        raise RuntimeError(
            "Python LiveReload is a development-only dependency; "
            "run the server through serve.sh or install it with "
            "'uv run --with livereload'."
        ) from exc
    return Server()


class DevServer:
    """Coordinate one long-lived builder, safe input polling, and LiveReload."""

    def __init__(
        self,
        source: Path,
        reporter: Reporter | None = None,
        *,
        builder: SiteBuilder | None = None,
        server_factory: Callable[[], Any] | None = None,
        watcher_factory: Callable[..., SourceWatcher] = SourceWatcher,
    ) -> None:
        self.source = source.resolve()
        self.output = self.source / "_site"
        self.reporter = reporter or Reporter()
        self.builder = (
            builder
            if builder is not None
            else SiteBuilder(self.source, reporter=self.reporter)
        )
        self.server_factory = server_factory or _create_livereload_server
        self.watcher_factory = watcher_factory
        self._build_lock = threading.Lock()

    def _output_snapshot(self) -> dict[str, tuple[int, int, int]]:
        if not self.output.is_dir():
            return {}
        return _file_snapshot(self.output, source_inputs=False)

    def _initial_build(self) -> bool:
        """Build once before the HTTP server starts."""
        try:
            self.builder.build()
            self.output.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            self.reporter.error("Initial site build failed: %s", exc)
            return False
        return True

    def rebuild(self, signal_file: Path) -> bool:
        """Run the existing incremental builder and signal only real success."""
        with self._build_lock:
            before = self._output_snapshot()
            try:
                self.builder.build()
            except Exception as exc:
                # A failed build may have written some outputs, but it must not
                # be announced as a successful refresh. The cache remains the
                # builder's responsibility and failed tasks will be retried.
                self.reporter.error("Incremental site build failed: %s", exc)
                return False

            after = self._output_snapshot()
            if before == after:
                self.reporter.info("Build completed; generated output is unchanged")
                return True

            try:
                signal_file.write_text(f"{time.time_ns()}\n", encoding="ascii")
            except OSError as exc:
                self.reporter.error(
                    "Build succeeded, but browser refresh could not be signalled: %s",
                    exc,
                )
                return False

            self.reporter.info("Build completed; browser refresh requested")
            return True

    def serve(
        self,
        *,
        host: str = _DEFAULT_HOST,
        port: int = _DEFAULT_PORT,
        liveport: int = _DEFAULT_LIVEPORT,
    ) -> int:
        """Run the initial build, then serve and watch until interrupted."""
        if port == liveport:
            self.reporter.error("HTTP port and LiveReload port must be different")
            return 2

        try:
            server = self.server_factory()
        except Exception as exc:
            self.reporter.error("%s", exc)
            return 1

        try:
            with tempfile.TemporaryDirectory(prefix="docbuild-livereload-") as temp:
                signal_file = Path(temp) / "reload.signal"
                signal_file.write_text("initial\n", encoding="ascii")
                server.watch(str(signal_file))

                watcher = self.watcher_factory(
                    self.source,
                    lambda: self.rebuild(signal_file),
                    self.reporter,
                )

                if not self._initial_build():
                    return 1

                watcher.start()
                self.reporter.info(
                    "Serving %s on http://%s:%d (LiveReload: %d)",
                    self.output,
                    host,
                    port,
                    liveport,
                )
                try:
                    server.serve(
                        port=port,
                        liveport=liveport,
                        host=host,
                        root=str(self.output),
                        debug=False,
                    )
                finally:
                    watcher.stop()
        except Exception as exc:
            self.reporter.error("Development server failed: %s", exc)
            return 1

        return 0


def _port(value: str) -> int:
    try:
        port = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("port must be an integer") from exc
    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError("port must be between 1 and 65535")
    return port


def main(argv: list[str] | None = None) -> int:
    """Run the development server command."""
    parser = argparse.ArgumentParser(
        description="Build and serve a docbuild site with incremental LiveReload."
    )
    parser.add_argument(
        "source_dir",
        nargs="?",
        default=".",
        help="source directory (default: current working directory)",
    )
    parser.add_argument(
        "--host",
        default=os.environ.get("HOST") or _DEFAULT_HOST,
        help=f"HTTP and LiveReload bind address (default: {_DEFAULT_HOST})",
    )
    parser.add_argument(
        "--port",
        type=_port,
        default=os.environ.get("PORT", str(_DEFAULT_PORT)),
        help=f"HTTP port (default: {_DEFAULT_PORT})",
    )
    parser.add_argument(
        "--liveport",
        type=_port,
        default=os.environ.get("LIVEPORT", str(_DEFAULT_LIVEPORT)),
        help=f"LiveReload WebSocket port (default: {_DEFAULT_LIVEPORT})",
    )
    args = parser.parse_args(argv)

    source = Path(args.source_dir).resolve()
    reporter = Reporter()
    if not source.is_dir():
        reporter.error("source directory does not exist: %s", source)
        return 2

    return DevServer(source, reporter=reporter).serve(
        host=args.host,
        port=args.port,
        liveport=args.liveport,
    )
