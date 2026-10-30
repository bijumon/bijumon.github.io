# Changelog

Notable changes to `docbuild`.

> The repository does not have tagged releases yet. Versions `0.1.0` through `0.5.0` below are retrospective development milestones inferred from Git history, not previously published releases. `0.6.0` is the current proposed version.

## 0.6.0 — Unreleased

### Added
- Add the optional `docbuild-serve` development command with a single initial build, incremental rebuilds, and LiveReload browser refresh.
- Add a symlink-safe polling watcher for source documents, static assets, templates, and configuration, with change coalescing and serialized builds.
- Use the existing dependency graph, incremental build planner, and SQLite cache for development rebuilds rather than introducing a separate invalidation mechanism.
- Refresh the browser only after a successful build changes generated output.
- Document the `make serve` workflow and configurable HTTP and LiveReload ports.

## 0.5.0 — Configuration and cache improvements

### Added
- Load site metadata from the required source-root `_config.toml`.
- Merge site-specific settings over generic, non-empty defaults.
- Add a version string to the site configuration defaults.
- Add configurable full-content hashing with a default 100 MiB file-size threshold; larger files use metadata signatures (`size`, `mtime_ns`, and `ctime_ns`).
- Add regression tests for same-size edits with restored timestamps, threshold validation, and the large-file metadata fallback.
- Add tests for defaults, overrides, missing configuration, malformed TOML, and template access.

### Changed
- Keep `content_hash_max_bytes` as an internal build setting rather than exposing it in template `site` metadata.
- Use generic defaults for author, site name, description, URL, and generator; real sites should define their own values in `_config.toml`.

## 0.4.0 — Markdown and source-discovery improvements

### Added
- Use Pandoc's CommonMark reader for Markdown documents.
- Enable pipe tables and footnotes for CommonMark.

### Fixed
- Skip symbolic links during source discovery to avoid traversing outside the source tree or following links back to ancestors.
- Add regression tests for the CommonMark options and symlink handling.

## 0.3.0 — Site page catalog

### Added
- Expose the complete page catalog through `site.pages` for use in Jinja2 templates, including filters such as `count` and `reverse`.
- Track shared site-context changes so pages can be rebuilt when the page catalog changes.

## 0.2.0 — Modular package and incremental builds

### Added
- Split the original build script into focused `docbuild` modules for discovery, conversion, frontmatter, indexing, caching, rendering, reporting, and build orchestration.
- Add an incremental file cache backed by Python's `dbm.sqlite3`.
- Avoid unnecessary document conversions and static-file copies when inputs have not changed.
- Regenerate missing outputs and retry failed conversions on subsequent builds.

### Changed
- Require Python 3.13 or newer.

## 0.1.0 — Initial Python build pipeline

### Added
- Introduce a Python-based static-site build pipeline using Pandoc and Jinja2.
- Render Markdown and Djot documents to HTML with frontmatter metadata and layout templates.
- Support Markdown and Djot document formats.
- Discover source documents, copy static assets, and keep generated output under `_site`.
- Add an initial unit-test suite for the builder.
