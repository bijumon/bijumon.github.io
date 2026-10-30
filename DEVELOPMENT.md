# Development workflow

## Build once

Run `make build` to perform a standalone production build. It uses the
published `ghcr.io/bijumon/pypandoc_alpine_uv:latest` image and writes the
generated site to `_site/`. It does not install or require LiveReload.

## Serve with incremental rebuilding

Run:

```sh
make serve
```

The `serve` service runs `docbuild-serve` inside the existing published
container image. It performs exactly one initial build before starting the
HTTP and LiveReload servers. It then serves `_site/` and watches build inputs.
LiveReload is installed for this invocation with `uv run --with livereload`;
it is not a mandatory docbuild dependency.

The source watcher polls without following symbolic links. It watches:

- Markdown and Djot documents and ordinary static assets discovered by docbuild.
- Files under `_templates/`, including nested templates.
- The root `_config.toml`.

It ignores `_site/`, SQLite cache files, Git metadata, hidden/private paths
(other than the explicit template and configuration exceptions), virtual
environments, tool caches, Python bytecode, and common editor temporary files.

Changes are debounced and builds are serialized. Each rebuild uses the same
long-lived `SiteBuilder`; the existing build graph, planner, and SQLite cache
remain responsible for determining which outputs need work. For example, a
static asset change copies that asset without converting documents, while a
shared template change rebuilds only dependent documents. The builder's
existing deletion policy is unchanged.

The browser refresh signal is emitted only after a successful build changes
the generated output. A failed build is reported through docbuild's
`Reporter`, does not stop the development server, and is not announced as a
successful refresh. The builder's cache behavior ensures failed outputs are
eligible for retry on the next build.

### Ports and container access

The default HTTP port is `8000`; the default LiveReload WebSocket port is
`35729`. Both ports are published by Compose. Override either from the host:

```sh
PORT=8080 LIVEPORT=35730 make serve
```

Then open `http://localhost:8080` (or use the host's LAN address to access
the container from another device). Ensure the selected ports are available
and allowed by the host firewall. The HTTP and LiveReload ports must differ.

You can also configure the bind address with `HOST` (default `0.0.0.0`).
The container listens on all interfaces so published ports are reachable.

### Command summary

| Command | Behavior |
| --- | --- |
| `make build` | One-shot production build; no LiveReload dependency |
| `make serve` | One initial build, HTTP server, safe file watcher, incremental rebuilds, browser refresh |
| `make test` | Run the Python test suite |
