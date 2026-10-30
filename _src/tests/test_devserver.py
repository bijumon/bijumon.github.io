from __future__ import annotations

import threading
from pathlib import Path
from unittest.mock import patch

import pytest

from docbuild.builder import SiteBuilder
from docbuild.devserver import DevServer, SourceWatcher
from docbuild.errors import BuildError


def _site(root: Path) -> None:
    (root / "_templates").mkdir()
    (root / "_templates" / "page.template").write_text(
        "<title>{{ site.name }}</title>{{ content }}",
        encoding="utf-8",
    )
    (root / "_config.toml").write_text('name = "Before"\n', encoding="utf-8")
    (root / "page.md").write_text("# First", encoding="utf-8")


def _poll_until_callback(watcher: SourceWatcher) -> bool:
    """Advance a deterministic two-poll debounce window."""
    watcher.poll_once(now=10.0)
    return watcher.poll_once(now=10.0 + watcher.debounce + 0.01)


@pytest.mark.parametrize(
    ("changed_path", "changed_content"),
    [
        ("page.md", "# Second"),
        ("_templates/page.template", "<h1>{{ site.name }}</h1>{{ content }}"),
        ("_config.toml", 'name = "After"\n'),
    ],
)
def test_document_template_and_config_changes_use_incremental_builder(
    tmp_path: Path,
    changed_path: str,
    changed_content: str,
) -> None:
    _site(tmp_path)
    builder = SiteBuilder(tmp_path)
    devserver = DevServer(tmp_path, builder=builder)
    signal = tmp_path / ".test-reload-signal"
    signal.write_text("initial\n", encoding="ascii")

    with patch(
        "docbuild.converter.pypandoc.convert_text",
        return_value="<p>Converted</p>",
    ) as convert:
        assert devserver._initial_build()
        watcher = SourceWatcher(
            tmp_path,
            lambda: devserver.rebuild(signal),
            debounce=0.1,
        )

        (tmp_path / changed_path).write_text(changed_content, encoding="utf-8")
        assert _poll_until_callback(watcher)
        assert devserver.builder is builder
        assert convert.call_count == 2


def test_static_asset_change_does_not_convert_documents(tmp_path: Path) -> None:
    _site(tmp_path)
    asset = tmp_path / "assets" / "site.css"
    asset.parent.mkdir()
    asset.write_text("body { color: black; }", encoding="utf-8")
    builder = SiteBuilder(tmp_path)
    devserver = DevServer(tmp_path, builder=builder)
    signal = tmp_path / ".test-reload-signal"
    signal.write_text("initial\n", encoding="ascii")

    with (
        patch(
            "docbuild.converter.pypandoc.convert_text",
            return_value="<p>Converted</p>",
        ) as convert,
        patch(
            "docbuild.builder.shutil.copy2",
            wraps=__import__("shutil").copy2,
        ) as copy,
    ):
        assert devserver._initial_build()
        convert.reset_mock()
        copy.reset_mock()

        watcher = SourceWatcher(
            tmp_path,
            lambda: devserver.rebuild(signal),
            debounce=0.1,
        )
        asset.write_text("body { color: white; }", encoding="utf-8")
        assert _poll_until_callback(watcher)

    convert.assert_not_called()
    copy.assert_called_once_with(asset, tmp_path / "_site" / "assets" / "site.css")
    assert (tmp_path / "_site" / "assets" / "site.css").read_text() == (
        "body { color: white; }"
    )


def test_only_successful_builds_with_changed_output_touch_reload_signal(
    tmp_path: Path,
) -> None:
    output = tmp_path / "_site"
    output.mkdir()
    generated = output / "page.html"
    generated.write_text("old", encoding="utf-8")
    signal = tmp_path / ".reload-signal"
    signal.write_text("initial\n", encoding="ascii")

    class Builder:
        def __init__(self) -> None:
            self.fail = False

        def build(self) -> None:
            generated.write_text("new", encoding="utf-8")
            if self.fail:
                raise BuildError("deliberate build failure")

    builder = Builder()
    devserver = DevServer(tmp_path, builder=builder)

    builder.fail = True
    assert not devserver.rebuild(signal)
    assert signal.read_text(encoding="ascii") == "initial\n"

    builder.fail = False
    assert devserver.rebuild(signal)
    assert signal.read_text(encoding="ascii") != "initial\n"


def test_irrelevant_paths_cache_and_output_are_excluded(tmp_path: Path) -> None:
    (tmp_path / "_config.toml").write_text("", encoding="utf-8")
    (tmp_path / "page.md").write_text("# Page", encoding="utf-8")
    watcher = SourceWatcher(tmp_path, lambda: pytest.fail("irrelevant path triggered"))

    (tmp_path / "_site").mkdir()
    (tmp_path / "_site" / "page.html").write_text("generated", encoding="utf-8")
    (tmp_path / ".cache.db").write_bytes(b"cache")
    (tmp_path / ".cache.db-wal").write_bytes(b"cache")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("git", encoding="utf-8")
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "pyvenv.cfg").write_text("venv", encoding="utf-8")
    (tmp_path / "venv").mkdir()
    (tmp_path / "venv" / "python").write_text("venv", encoding="utf-8")
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "module.pyc").write_bytes(b"bytecode")
    (tmp_path / "page.md.swp").write_text("swap", encoding="utf-8")
    (tmp_path / "page.md~").write_text("backup", encoding="utf-8")
    (tmp_path / "_drafts").mkdir()
    (tmp_path / "_drafts" / "draft.md").write_text("# Draft", encoding="utf-8")

    # The snapshot applies the same exclusion rules after these paths exist.
    watcher._snapshot = watcher.snapshot()
    (tmp_path / "_site" / "page.html").write_text("changed", encoding="utf-8")
    (tmp_path / ".cache.db").write_bytes(b"changed")
    (tmp_path / ".git" / "config").write_text("changed", encoding="utf-8")
    (tmp_path / ".venv" / "pyvenv.cfg").write_text("changed", encoding="utf-8")
    (tmp_path / "venv" / "python").write_text("changed", encoding="utf-8")
    (tmp_path / "__pycache__" / "module.pyc").write_bytes(b"changed")
    (tmp_path / "page.md.swp").write_text("changed", encoding="utf-8")
    (tmp_path / "_drafts" / "draft.md").write_text("# Changed", encoding="utf-8")

    assert watcher.snapshot() == watcher._snapshot
    assert not watcher.poll_once(now=20.0)


def test_watcher_includes_only_config_templates_and_discovered_inputs(
    tmp_path: Path,
) -> None:
    (tmp_path / "_config.toml").write_text("", encoding="utf-8")
    (tmp_path / "_templates").mkdir()
    (tmp_path / "_templates" / "base.template").write_text("base", encoding="utf-8")
    (tmp_path / "_templates" / "partials").mkdir()
    (tmp_path / "_templates" / "partials" / "nav.template").write_text(
        "nav", encoding="utf-8"
    )
    (tmp_path / "page.djot").write_text("page", encoding="utf-8")
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "image.png").write_bytes(b"image")
    (tmp_path / "_private").mkdir()
    (tmp_path / "_private" / "secret.md").write_text("secret", encoding="utf-8")
    (tmp_path / ".hidden.md").write_text("hidden", encoding="utf-8")

    snapshot = SourceWatcher(tmp_path, lambda: None).snapshot()

    assert set(snapshot) == {
        "_config.toml",
        "_templates/base.template",
        "_templates/partials/nav.template",
        "assets/image.png",
        "page.djot",
    }


def test_watcher_does_not_follow_file_directory_or_ancestor_symlinks(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "page.md").write_text("# Page", encoding="utf-8")
    nested = source / "nested"
    nested.mkdir()
    (nested / "inside.md").write_text("# Inside", encoding="utf-8")

    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.md").write_text("# Secret", encoding="utf-8")

    try:
        (source / "outside-link").symlink_to(outside, target_is_directory=True)
        (source / "nested" / "back-to-source").symlink_to(
            source, target_is_directory=True
        )
        (source / "file-link.md").symlink_to(outside / "secret.md")
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"symbolic links are not supported in this environment: {exc}")

    snapshot = SourceWatcher(source, lambda: None).snapshot()

    assert set(snapshot) == {"page.md", "nested/inside.md"}


def test_watcher_detects_new_files_deleted_files_renames_and_nested_creation(
    tmp_path: Path,
) -> None:
    (tmp_path / "_config.toml").write_text("", encoding="utf-8")
    calls: list[str] = []
    watcher = SourceWatcher(
        tmp_path,
        lambda: calls.append("build"),
        debounce=0,
    )

    nested = tmp_path / "new" / "nested"
    nested.mkdir(parents=True)
    created = nested / "new.md"
    created.write_text("# New", encoding="utf-8")
    assert _poll_until_callback(watcher)
    assert calls == ["build"]

    renamed = nested / "renamed.md"
    created.rename(renamed)
    assert _poll_until_callback(watcher)
    assert calls == ["build", "build"]

    renamed.unlink()
    assert _poll_until_callback(watcher)
    assert calls == ["build", "build", "build"]


def test_watcher_coalesces_multiple_events_until_debounce_expires(
    tmp_path: Path,
) -> None:
    (tmp_path / "_config.toml").write_text("", encoding="utf-8")
    page = tmp_path / "page.md"
    page.write_text("# One", encoding="utf-8")
    calls: list[str] = []
    watcher = SourceWatcher(
        tmp_path,
        lambda: calls.append("build"),
        debounce=0.5,
    )

    page.write_text("# Two", encoding="utf-8")
    assert not watcher.poll_once(now=1.0)
    page.write_text("# Three", encoding="utf-8")
    assert not watcher.poll_once(now=1.3)
    assert not watcher.poll_once(now=1.7)
    assert watcher.poll_once(now=1.81)
    assert calls == ["build"]
    assert not watcher.poll_once(now=2.5)
    assert calls == ["build"]


def test_concurrent_rebuilds_are_serialized(tmp_path: Path) -> None:
    output = tmp_path / "_site"
    entered = threading.Event()
    release = threading.Event()
    state_lock = threading.Lock()

    class BlockingBuilder:
        def __init__(self) -> None:
            self.active = 0
            self.maximum_active = 0
            self.calls = 0

        def build(self) -> None:
            with state_lock:
                self.active += 1
                self.maximum_active = max(self.maximum_active, self.active)
                self.calls += 1
                call_number = self.calls
            if call_number == 1:
                entered.set()
                assert release.wait(timeout=2)
            output.mkdir(parents=True, exist_ok=True)
            (output / "page.html").write_text(str(call_number), encoding="utf-8")
            with state_lock:
                self.active -= 1

    builder = BlockingBuilder()
    devserver = DevServer(tmp_path, builder=builder)
    signal = tmp_path / ".reload-signal"
    signal.write_text("initial\n", encoding="ascii")

    first = threading.Thread(target=devserver.rebuild, args=(signal,))
    second = threading.Thread(target=devserver.rebuild, args=(signal,))
    first.start()
    assert entered.wait(timeout=2)
    second.start()
    release.set()
    first.join(timeout=2)
    second.join(timeout=2)

    assert not first.is_alive()
    assert not second.is_alive()
    assert builder.calls == 2
    assert builder.maximum_active == 1


def test_initial_build_happens_once_before_serving(tmp_path: Path) -> None:
    events: list[str] = []

    class Builder:
        def build(self) -> None:
            events.append("build")

    class Server:
        signal_path: str | None = None

        def watch(self, path: str) -> None:
            self.signal_path = path

        def serve(self, **kwargs: object) -> None:
            events.append("serve")
            assert kwargs["root"] == str(tmp_path / "_site")

    class Watcher:
        def __init__(self, source: Path, callback: object, reporter: object) -> None:
            self.callback = callback

        def start(self) -> None:
            events.append("watch")

        def stop(self) -> None:
            events.append("stop")

    server = Server()
    devserver = DevServer(
        tmp_path,
        builder=Builder(),
        server_factory=lambda: server,
        watcher_factory=Watcher,
    )

    assert devserver.serve(port=8000, liveport=35729) == 0
    assert events == ["build", "watch", "serve", "stop"]
    assert server.signal_path is not None
    assert Path(server.signal_path).is_file()


def test_failed_rebuild_does_not_stop_development_server(tmp_path: Path) -> None:
    output = tmp_path / "_site"
    signal_contents: list[str] = []

    class Builder:
        calls = 0

        def build(self) -> None:
            self.calls += 1
            output.mkdir(parents=True, exist_ok=True)
            if self.calls == 1:
                (output / "page.html").write_text("initial", encoding="utf-8")
                return
            (output / "partial.html").write_text("partial", encoding="utf-8")
            raise BuildError("deliberate failure")

    class Server:
        signal_path: str | None = None
        served = False

        def watch(self, path: str) -> None:
            self.signal_path = path

        def serve(self, **kwargs: object) -> None:
            self.served = True
            assert self.signal_path is not None
            signal_contents.append(
                Path(self.signal_path).read_text(encoding="ascii")
            )

    class TriggeringWatcher:
        def __init__(self, source: Path, callback: object, reporter: object) -> None:
            self.callback = callback

        def start(self) -> None:
            self.callback()  # type: ignore[operator]

        def stop(self) -> None:
            pass

    server = Server()
    builder = Builder()
    devserver = DevServer(
        tmp_path,
        builder=builder,
        server_factory=lambda: server,
        watcher_factory=TriggeringWatcher,
    )

    assert devserver.serve() == 0
    assert builder.calls == 2
    assert server.served
    assert signal_contents == ["initial\n"]


def test_same_site_builder_instance_handles_repeated_builds(tmp_path: Path) -> None:
    _site(tmp_path)
    builder = SiteBuilder(tmp_path)
    devserver = DevServer(tmp_path, builder=builder)
    signal = tmp_path / ".reload-signal"
    signal.write_text("initial\n", encoding="ascii")

    with patch(
        "docbuild.converter.pypandoc.convert_text",
        return_value="<p>Body</p>",
    ) as convert:
        assert devserver._initial_build()
        first = (tmp_path / "_site" / "page.html").read_text(encoding="utf-8")

        (tmp_path / "page.md").write_text("# Updated", encoding="utf-8")
        assert devserver.rebuild(signal)
        second = (tmp_path / "_site" / "page.html").read_text(encoding="utf-8")

    assert devserver.builder is builder
    assert first == second
    assert convert.call_count == 2
