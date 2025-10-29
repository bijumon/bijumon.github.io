---
---

# **SSGv3 Design**

## *Architecture & Core Principles*

SSGv3 is a static site generator built around a **three-stage pipeline** designed for safety, incremental speed, and deterministic outputs:

```
SCAN → BUILD → WRITE
```

Each stage has **clear boundaries**:

| Stage          | Reads File Contents?     | Transforms / Renders? | Writes Output? | Purpose                                               |
| -------------- | ------------------------ | --------------------- | -------------- | ----------------------------------------------------- |
| **ScanStage**  | No                       | No                    | No             | Discover source files and infer initial metadata      |
| **BuildStage** | Yes (only changed items) | Yes                   | No             | Convert content → HTML and fully resolve output paths |
| **WriteStage** | No additional reads      | No                    | Yes            | Atomically commit outputs and update cache            |

This guarantees that:

* **No partial site output** is ever written (atomic write rules)
* **All failures occur before writing**
* **Incremental builds** only reprocess items that changed or depend on changed templates/config

---

## **Core Representations**

### **BuildItem**

Every file discovered becomes a **BuildItem**, which may later become:

* **ContentItem** (produced from markdown, templated, generates HTML)
* **AssetItem** (copied byte-for-byte to output)
* **IndexItem** (virtual: generated for index pages / pagination)

Each item carries:

```
src → original source path (if any)
out → final output path (resolved in BuildStage)
kind → content | asset | index | feed
state → SCANNED | BUILT | WRITTEN
metadata → resolved metadata (after merges and overrides)
```

---

## **Metadata Resolution Rules**

Metadata comes from **three sources**, applied in this precedence order:

1. **System defaults**
   (`slug=filename`, `category=parent directory`, inferred `date` if possible)
2. **Directory- / filename-derived metadata**
   Used only **if not overridden in frontmatter**
3. **Frontmatter overrides**
   Always take precedence if explicitly set.

This means:

| Situation                                                                   | Result                                      |
| --------------------------------------------------------------------------- | ------------------------------------------- |
| File moved to a new category directory, **no frontmatter category present** | Category changes (and URL changes)          |
| File moved but **frontmatter specifies category**                           | Category does **not** change                |
| User explicitly sets slug/date                                              | URL remains stable even if filename changes |

This allows stable URLs **when desired**, without removing the convenience of folder-based organization.

---

## **Template Selection Strategy**

SSGv3 chooses templates as follows:

1. If frontmatter explicitly says `template: X`, use `X`
2. Otherwise, if category is `python`, and `templates/python.html` exists → use it
3. Otherwise → use `templates/default.html` (required)

This delivers:

* Category-specific layouts automatically
* Overridable behavior without boilerplate
* Stable template cache invalidation (template hashes tracked)

---

## **Permalink & Output Path Behavior**

Permalink generation uses named placeholders:

```
{category}/{year}/{month}/{slug}/
```

Supported placeholders: `{year}`, `{month}`, `{day}`, `{slug}`, `{category}`
With formatting rules like `:02d`.

Example resolved URL:

```
/python/2025/10/my-post/
→ output written to
public/python/2025/10/my-post/index.html
```

### **Collision Detection**

BuildStage detects when two items produce the same URL.
If collision occurs → **build fails before WriteStage.**

---

## **Pagination Model (H1)**

Main index pagination:

```
/index.html
/page/2/index.html
/page/3/index.html
...
```

Category pagination:

```
/python/index.html
/python/page/2/index.html
...
```

No ambiguous directories. Works on all static hosts with no rewrite rules.

---

## **Template Selection Strategy**

SSGv3 chooses templates as follows:

1. If frontmatter explicitly says `template: X`, use `X`
2. Otherwise, if category is `python`, and `templates/python.html` exists → use it
3. Otherwise → use `templates/default.html` (required)

This delivers:

* Category-specific layouts automatically
* Overridable behavior without boilerplate
* Stable template cache invalidation (template hashes tracked)

---

## **Permalink & Output Path Behavior**

Permalink generation uses named placeholders:

```
{category}/{year}/{month}/{slug}/
```

Supported placeholders: `{year}`, `{month}`, `{day}`, `{slug}`, `{category}`
With formatting rules like `:02d`.

Example resolved URL:

```
/python/2025/10/my-post/
→ output written to
public/python/2025/10/my-post/index.html
```

### **Collision Detection**

BuildStage detects when two items produce the same URL.
If collision occurs → **build fails before WriteStage.**

---

## **Pagination Model (H1)**

Main index pagination:

```
/index.html
/page/2/index.html
/page/3/index.html
...
```

Category pagination:

```
/python/index.html
/python/page/2/index.html
...
```

No ambiguous directories. Works on all static hosts with no rewrite rules.

---

## ScanStage — Pure Discovery & BuildItem Construction

ScanStage performs a **fast, side-effect-free traversal** of the source tree(s) and produces an initial set of `BuildItem` objects that feed into BuildStage. It should do **no content parsing** and **no file reads beyond metadata/stat**.

---

## Inputs

* `Config` (paths + blacklist + extensions + output/cache dir)
* `previous_manifest` (optional, for determining deletions in later stages)
* filesystem root (project root or `--source-dir`)

---

## Outputs

* `BuildContext.items` — list of `BuildItem(state=SCANNED)` with minimal metadata:

  * `src: Path`
  * `kind: 'content' | 'asset'`
  * `initial_slug: str` (filename without extension)
  * `initial_category: str | ''` (immediate parent dir name; empty if top-level)
  * `stat` info: `mtime`, `size`
  * `path_rel`: source path relative to `content_dir` or `asset_dir`

No `html`, no `templates_used`, no rendered metadata.

---

## Discovery Algorithm (step-by-step)

1. **Resolve configured directories**

   * `content_dir`, `asset_dir`, `template_dir`, `output_dir`, `cache_dir` → absolute `Path`s.

2. **Build ignore set** (ordered precedence)

   1. `output_dir` and `cache_dir` — always ignore
   2. `Config.blacklist` entries — treat as path prefixes relative to `source_dir`
   3. Dot directories like `.git`, `.venv`, `.cache` — default ignore unless explicitly whitelisted
   4. Files with names starting with `.` (dotfiles) — ignored by default
   5. Platform-specific temporary files (e.g., `~`, `.DS_Store`) — optional entries in blacklist

3. **Walk directories**

   * Use `os.scandir` or `Path.rglob` with manual pruning for efficiency.
   * For each entry:

     * If directory → skip descending into ignored paths.
     * If file → determine kind:

       * If extension in `config.content_extensions` → `kind='content'`
       * Otherwise → `kind='asset'` (unless asset blacklisted)
     * Compute `path_rel` = path relative to its root directory (content_dir/asset_dir).
     * Derive `initial_slug` = `filename_without_extension`

       * Normalization: unicode NFC, collapse whitespace, do not yet slug-ify (slugify happens in BuildStage).
     * Derive `initial_category`:

       * If `path_rel` has parent → `parent.name`
       * Else `''` (empty string)
     * Stat the file: `mtime`, `size` — minimal I/O
     * Construct `BuildItem(state=SCANNED, src=abs_path, kind=..., metadata={initial_slug, initial_category}, stat=...)`
     * Append to `context.items`

4. **Special files recognition**

   * Files named `index.md` are still content items, but note that they may influence category index page generation later.
   * If a file `README.md` exists in a directory, treat as regular content — BuildStage will decide semantics.
   * Hidden but explicitly whitelisted files (via config) should be included.

5. **Return** `context.items` in a deterministic (sorted) order – e.g., sorted by `path_rel` to make reproducible builds and easier testing.

---

## Performance & Safety Notes

* Use streaming directory walk (avoid building huge in-memory file lists if unnecessary).
* Prune early using ignore set to reduce I/O.
* Do **not** follow symlinks by default (configurable option `follow_symlinks = false`) — following symlinks can cause loops or unexpected duplication.
* Do not open or read file bytes here — only `stat()`.

---

## Edge Cases & How ScanStage Handles Them

1. **File moved between runs**

   * ScanStage will reflect new path; BuildStage decides whether the effective URL changes (based on frontmatter presence per Option 3).

2. **Conflicting names across content/asset roots**

   * If same relative path occurs in both `content_dir` and `asset_dir`, both items are included; collision detection later compares generated URLs and output paths.

3. **Files with unusual encodings**

   * ScanStage ignores encodings. Encoding problems surface only in BuildStage when content is read.

4. **Multiple content directory roots**

   * Config may allow multiple content roots; ScanStage treats them as independent roots but keeps `path_rel` relative to their root to derive category consistently.

5. **Blacklisted nested rules**

   * Blacklist entries are treated as prefixes; `blacklist=['drafts/']` prunes any path starting with `drafts/`.

6. **Large repositories**

   * Optionally return an iterator of BuildItems instead of full list for memory-constrained environments, but note BuildStage expects full set to detect URL collisions and build indexes deterministically.

---

## Deterministic Ordering & Idempotence

* Always sort discovered items by their `path_rel` (and root type) with a stable comparator.
* Deterministic ordering ensures same BuildStage behavior across runs and supports reliable caching.

---

## Tests to Verify ScanStage

1. **Basic discovery**

   * Given small sample tree, assert exact set of `BuildItem`s and their `initial_slug`/`initial_category`.

2. **Ignore rules**

   * Place files in `.git/`, `output_dir/`, and `content/drafts/` and ensure they are excluded.

3. **Symlink behavior**

   * With `follow_symlinks=false`, ensure symlinked files are not traversed.

4. **Multiple roots**

   * Configure two content roots and validate `path_rel` and category derivation are correct per root.

5. **Order determinism**

   * Run discovery twice without changes, ensure returned lists are identical.

---

## Minimal Data Contract (BuildItem in ScanStage)

```python
@dataclass
class BuildItem:
    src: Path
    kind: Literal['content', 'asset']
    path_rel: Path  # relative to the root it was discovered in
    initial_slug: str
    initial_category: str  # immediate parent or ''
    stat: FileStat  # mtime, size
    state: Literal['SCANNED']
```

---

## Example Output (from sample tree)

Input:

```
content/python/intro.md
content/rust/ownership.md
assets/css/style.css
```

ScanStage produces:

```
[
  BuildItem(src='.../content/python/intro.md', kind='content', path_rel='python/intro.md', initial_slug='intro', initial_category='python', stat=...),
  BuildItem(src='.../content/rust/ownership.md', kind='content', path_rel='rust/ownership.md', initial_slug='ownership', initial_category='rust', stat=...),
  BuildItem(src='.../assets/css/style.css', kind='asset', path_rel='css/style.css', initial_slug='style', initial_category='css', stat=...)
]
```

---

## BuildStage

BuildStage takes the `BuildItem(state=SCANNED)` list from ScanStage and produces a **complete, in-memory representation** for every output the system will write. It must:

* Read file contents **only when necessary**
* Parse frontmatter and merge metadata according to the precedence rules
* Convert Markdown → HTML exactly once per changed item (M1)
* Render templates to final HTML (in-memory)
* Compute deterministic cache keys and consult the cache
* Build the `url -> src` mapping for collision detection
* Create virtual `IndexItem`s for pages (these are treated as built items too)
* Collect all errors; **do not write anything** if any error exists

---

## Preconditions & Inputs

* `context.items` (list of BuildItems from ScanStage)
* `Config` (permalink templates, markdown config, page_size, etc.)
* `Manifest` (previous build manifest + template hashes)
* `Services` (TemplateRenderer, CacheManager, MetadataExtractor, PermalinkGenerator, OutputWriter (not used here))

---

## High-Level Flow (concise)

1. Call `processor.before_build(context)` for all processors (read-only init).
2. For each `BuildItem`:

   * Determine `resolved_metadata` via MetadataExtractor (merging defaults, directory-derived, frontmatter)
   * Choose template per T2 rules (frontmatter > category template > default)
   * Compute `item_cache_key` (deterministic SHA256 over a JSON object — see formula)
   * If `CacheManager.needs_processing(src, item_cache_key)` is `False` → load cached `ContentItem` (metadata + html) and mark as `BUILT`.
   * Else → read file bytes, parse frontmatter, transform Markdown → HTML (M1), render template (TemplateRenderer.render) producing `html`, capture `templates_used`, produce `ContentItem(state=BUILT)` in memory.
3. After all items processed, generate virtual `IndexItem`s (main paginated index + category paginated indexes) in memory and add to `items`.
4. Generate `url_map` for every `BUILT` item (content + indexes + feeds).
5. Detect collisions in `url_map`. If any collisions → add structured `BuildError` entries.
6. If any errors found → return error list and abort before WriteStage. Otherwise return `List[BuildItem(state=BUILT)]`.

---

## Metadata Extraction & Merging (precise sequence)

For a content file `src`:

1. **System defaults**

   * `initial_slug` from ScanStage (filename without ext)
   * `initial_category` from ScanStage (parent folder name or empty)
   * `date` default = file `stat.mtime` (as naive datetime UTC-local conversion)
2. **Directory-derived**

   * Derived only if not present in frontmatter; included in `resolved_metadata` but marked as `derived_from='path'`
3. **Frontmatter overrides**

   * Parsed with `python-frontmatter` or equivalent (YAML/TOML auto-detect)
   * Any explicitly present field wins and is marked `derived_from='frontmatter'`
4. **Final resolved metadata** includes:

   * `slug` (normalized, URL-safe slugify applied here)
   * `title`
   * `date` (ISO format stored as `date_iso`)
   * `category`
   * `tags` (list)
   * `template` (if provided)
   * any other frontmatter keys forwarded to template context

**Slug normalization rules**

* Lowercase, ASCII-fallback (transliterate Unicode), remove punctuation except `-`, collapse whitespace to `-`, strip leading/trailing `-`.
* For languages requiring preserving diacritics, allow config toggle `slug_preserve_unicode: bool`.

**Date parsing**

* Accept many human formats (use `dateutil.parser.parse`)
* If timezone present, normalize to UTC then store naive ISO (configurable; default: store ISO with offset removed but keep `date_iso = aware.isoformat()` if `config.preserve_timezone=true`).

---

## Cache Key — Deterministic Hash Formula

**Goal:** Include everything that should invalidate a previously-rendered result.

Compute keys as:

```python
keyobj = {
  "content_hash": sha256(file_content_bytes).hexdigest() if src else None,
  "processor_id": processor.id,
  "selected_template_hash": template_renderer.get_template_hash(selected_template_name),
  "permalink_template_hash": sha256(config.permalink_templates_serialized),
  "metadata_parts": {
    "slug": resolved_slug,
    "category": resolved_category,
    "date_iso": resolved_date_iso
  },
  "config_version": config.cache_schema_version  # bump on breaking config changes
}
cache_key = sha256(json.dumps(keyobj, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()
```

**Notes**

* For virtual items (IndexItem) `content_hash` may be `None` and `metadata_parts` should include page number and list of contributing item keys (or a digest thereof).
* `selected_template_hash` must include partials/includes recursively (TemplateRenderer must provide this).
* `permalink_template_hash` prevents stale URL changes when permalink template changes.

---

## Cache Interaction & Safe Skips

* `CacheManager.needs_processing(src, cache_key)` returns `True` when no entry exists or the stored key differs.
* On cache hit → `CacheManager.load_metadata(src)` must return:

  * final `out` path
  * rendered `html`
  * `templates_used`
  * saved `metadata` (slug/date/category)
* **Sanity check on cache hit**: re-derive URL from cached metadata and ensure `perm_gen.generate(cached_metadata)` == cached `url`. If mismatch (rare), treat as cache miss to be safe.

---

## Markdown → HTML (M1) & Template Rendering

* Use a configurable Markdown library (e.g., `markdown` with `extensions` from config).
* Process flow for changed items:

  1. Read file bytes (try UTF-8, fallback to latin-1; log encoding fallback warning).
  2. Frontmatter parsed (YAML/TOML). Any parse errors → structured `BuildError`.
  3. Markdown body → HTML (single pass).
  4. Template context assembled:

     ```
     ctx = {
       "content": html_body,
       "metadata": resolved_metadata,
       "site": config.site,
       "page": pagination_meta_if_any
     }
     ```
  5. Render `selected_template` via `TemplateRenderer.render(name, ctx)` → `final_html`.
  6. `TemplateRenderer` records which templates/partials were accessed for `templates_used`.

**Important:** TemplateRenderer must not write files in BuildStage. Any precompilation for speed must be read-only.

---

## Template Dependency Tracking

* `templates_used` list must include every template file path consumed (including partials).
* `CacheManager.mark_processed(item, cache_key)` persists `templates_used` for reverse lookup.
* When a template file changes (its `get_template_hash` differs from manifest), the system queries `CacheManager.get_items_using_template(template_path)` to mark affected items as needing rebuild.

---

## Permalink Generation & Output Path Resolution

* `PermalinkGenerator.generate(resolved_metadata)` returns:

  * `url` (site-relative path ending with `/`, e.g. `/python/2025/10/foo/`)
  * `out` (filesystem path: `<output_dir>/<url>/index.html`)
* `BuildStage` sets `item.out` and `item.url` accordingly.
* For pages with direct filenames (e.g., assets) the generator returns file path mapping directly.

---

## URL Collision Detection

1. Maintain `url_map: Dict[str, List[BuildItem.src]]`.
2. After generating URLs for all content items and virtual IndexItems, identify keys where `len(list) > 1`.
3. For each collision, create a `BuildError` with:

   * `code: 'URL_COLLISION'`
   * `url`
   * `sources: list of src paths`
   * `suggestions: override slug or category in frontmatter, or change permalink template`
4. Collisions cause BuildStage to fail (no writes).

**Special-case rules**

* Directory `index.html` vs content slug: e.g., a category index `/python/` colliding with a content item that resolves to `/python/`. Treat as collision.
* Trailing slash normalization is enforced; collisions must be checked with normalized URLs.

---

## IndexItem Creation (in BuildStage, virtual)

After building content items, build virtual IndexItems with intelligent rebuild detection:

### Index Types & Generation

* **Main index**: paginated per `page_size`, sorted by `date_iso` desc
* **Category indexes**: per category, same pagination rules
* Each IndexItem gets `out`/`url` assigned (e.g., `/page/2/` or `/python/page/2/`)

### Index Rebuild Triggers (Precise Rules)

An index page must be rebuilt if ANY of the following changed since last build:

1. **Membership change**: Any item added/removed from the index's item set
2. **Ordering change**: Any included item's sort key (`date_iso`) changed
3. **Metadata change**: Any included item's title, excerpt, or template-visible metadata changed
4. **Template change**: The index template or its partials were modified
5. **Pagination boundary shift**: Items moved between pages (e.g., post count changed causing page 2 to now show different items)

### Index Cache Key Computation

IndexItem cache keys depend on:

```python
index_keyobj = {
  "index_type": "main" | f"category:{category_name}",
  "page_num": N,
  "template_hash": template_renderer.get_template_hash('index.html'),
  "items_digest": sha256(json.dumps([
    {
      "cache_key": item.cache_key,
      "date_iso": item.metadata['date_iso'],
      "url": item.url
    }
    for item in items_on_this_page
  ], sort_keys=True).encode()).hexdigest(),
  "total_pages": total_page_count,
  "config_version": config.cache_schema_version
}
index_cache_key = sha256(json.dumps(index_keyobj, sort_keys=True).encode()).hexdigest()
```

**Key insight**: `items_digest` captures both membership AND ordering because it includes sorted list of item cache keys + date + url. Any change to constituent items invalidates the index page.

### Optimization for Large Sites

For sites with >1000 posts where most pages remain stable:

1. Compute `items_digest` for each page separately
2. Cache hit on page N if:
   - `items_digest` matches cached value
   - `total_pages` unchanged (no pagination boundary shift)
   - `template_hash` unchanged
3. Only rebuild pages where digest differs

This allows incremental index updates: changing post #500 rebuilds only the page(s) containing it, not all 100 pages.

### IndexItem Construction

```python
for page_num, items_chunk in paginate(sorted_items, page_size):
    index_item = IndexItem(
        kind='index',
        state='BUILT',
        url=f'/page/{page_num}/' if page_num > 1 else '/',
        out=output_dir / ('index.html' if page_num == 1 else f'page/{page_num}/index.html'),
        cache_key=compute_index_cache_key(items_chunk, page_num, total_pages),
        html=render_if_cache_miss(template='index.html', context={...}),
        templates_used=['templates/index.html', ...]
    )
    context.items.append(index_item)
```

IndexItems participate in collision detection like regular content items.

---

## Error Collection & Reporting

* `BuildError` structure:

```json
{
  "code": "FRONTMATTER_PARSE_ERROR",
  "src": "content/python/bad.md",
  "message": "Failed to parse frontmatter: ...",
  "suggestion": "Check YAML syntax at line X",
  "trace": "..." (optional)
}
```

* Errors are accumulated in a list. At end of BuildStage, if list not empty:

  * Print a human-friendly summary (count + examples)
  * Return errors to pipeline runner -> abort WriteStage
* Examples of errors:

  * Invalid frontmatter (syntax)
  * Unsupported date format (if fallback disallowed)
  * Missing required metadata (e.g., `slug` if permissive mode disabled)
  * Template not found (when `default.html` missing)
  * URL collisions

---

## Performance & Memory Notes

* BuildStage holds `html` for all built items in memory. For very large sites:

  * Option: stream already-rendered HTML to temporary files but still treat them as built until write swap (advanced).
  * Default mode assumes memory budget ~ 5–20 MB per 1000 posts depending on HTML size; document recommended hardware targets in Appendix.

---

## Tests to Validate BuildStage

1. **Cache hit stability**

   * Build once, touch unrelated file, rebuild; assert cache hits for unchanged items.

2. **Frontmatter override behavior**

   * File with `category: custom` moved across directories → assert URL unchanged.

3. **Template change invalidation**

   * Change a partial included by `python.html` → assert only items that used that template are rebuilt.

4. **URL collision detection**

   * Create two files that resolve to same slug+category → assert BuildStage fails with proper collision error.

5. **Index pagination correctness**

   * For 25 posts with `page_size=10`, assert `/index.html`, `/page/2/index.html`, `/page/3/index.html` created as IndexItems with correct counts.

6. **Encoding fallback**

   * File with latin-1 bytes → ensure read fallback works and a warning is logged.

---

## Example Walkthrough (concise)

* `ScanStage` produced `content/python/foo.md` (initial_slug `foo`, initial_category `python`).
* BuildStage:

  * Parse frontmatter → no `category` field; resolve `category=python`.
  * Slugize `foo` → `foo`.
  * Template selection: `templates/python.html` exists → use it.
  * Compute cache_key with content hash + `python.html` template hash + metadata parts.
  * Cache miss → read file, parse markdown → HTML, render final template → store `final_html` and `templates_used`.
  * PermalinkGenerator yields `/python/2025/10/28/foo/` → set `item.out = public/python/2025/10/28/foo/index.html`.
  * Add to `url_map`.
* After all items: detect no collisions → BuildStage returns built items for WriteStage.

---

## WriteStage

WriteStage is the only stage that performs side effects. Its goals:

* Atomically publish a new site output that is consistent and complete.
* Update the cache/manifest on success.
* Remove orphaned outputs from the previous build safely.
* Never leave the live output directory in a partially-updated state on success.
* Provide clear rollback and retry behavior on failures.

---

## High-level WriteStage Flow (summary)

1. Verify BuildStage returned zero errors and provided `List[BuildItem(state=BUILT)]`.
2. Call `processor.before_write(context)` for all processors (finalization hooks).
3. Create temporary output directory `output_dir_tmp`.
4. Write every BuiltItem into `output_dir_tmp` (use OutputWriter; see API below).
5. Flush and verify all writes succeeded.
6. Persist new `manifest.json` into `cache_dir` atomically.
7. Atomically replace current `output_dir` with `output_dir_tmp`.
8. Post-swap: call `processor.after_write(context)` for any post-publish work.
9. Delete old output (if using swap) or delete orphaned files based on manifest diff (manifest-driven).
10. Return success and stats.

If any step fails, apply rollback rules (below) and return an appropriate error code.

---

## Atomic Publish Strategies (configurable)

SSGv3 supports two safe modes. Default is **Atomic Directory Swap**; fallback is **Manifest-driven Overwrite**.

### Strategy A — Atomic Directory Swap (recommended)

**Approach**

* Write everything into `output_dir_tmp` (sibling of `output_dir`, e.g. `public.__tmp_20251028_1234`).
* Once all writes succeed, rename current `output_dir` → `output_dir_old_<ts>` (if exists), then rename `output_dir_tmp` → `output_dir`.
* Remove old `output_dir_old_<ts>` after success (or keep for quick rollback if configured).

**Pros**

* Strong atomicity: `output_dir` is switched in a single rename/move operation.
* Clients reading from `output_dir` never see partially written site.

**Cons & Mitigations**

* Requires disk capacity ≥ current output + new output temporarily. Offer fallback mode.
* Platform rename semantics: `os.replace()` works for file-level; directory atomicity depends on filesystem — document supported platforms.

**Notes**

* On Linux, a `rename` of directory within same parent is atomic. On Windows, moving directories may have different semantics — use file-by-file replace as a fallback on Windows if necessary.

### Strategy B — Manifest-driven Overwrite (low-disk)

**Approach**

* Write each new file to `output_dir` using a `.tmp` suffix or temporary path (e.g., `public/path/file.html.tmp`).
* Once file write completes, atomically rename file `.tmp` → final name.
* After all files are renamed, write new `manifest.json`.
* Compute orphans by diffing previous manifest and new manifest; delete orphans.

**Pros**

* Lower peak disk usage.
* Works better on constrained systems.

**Cons**

* More complex to reason about partial failures.
* Requires careful ordering (write & rename all files before updating manifest).

**Safety**

* Ensure `manifest.json` is the authoritative indicator of which files belong to the current build; only delete orphans after manifest update and verification.

---

## OutputWriter — API & Guarantees

`OutputWriter` is the single place for filesystem writes. WriteStage uses it exclusively.

### Interface

```python
class OutputWriter(ABC):
    def ensure_directory(self, path: Path) -> None
    def write_bytes(self, dest: Path, data: bytes) -> None
    def write_text(self, dest: Path, text: str, encoding='utf-8') -> None
    def copy_file(self, src: Path, dest: Path, preserve_mtime: bool=True) -> None
    def atomic_rename(self, src: Path, dest: Path) -> None
    def remove(self, path: Path) -> None
    def replace_directory_atomic(self, src_dir: Path, dest_dir: Path) -> None
```

### Semantics & Implementation notes

* `write_*` should write to a temporary file (same directory) then fsync and rename to final name to reduce partial-read exposure.
* `atomic_rename` must use platform primitives (`os.replace` or equivalent) and raise on failure.
* `replace_directory_atomic` implements the atomic swap (if supported) or a safe fallback procedure:

  * Create `dest_dir_tmp`, write content there, then `os.replace(dest_dir_tmp, dest_dir)`
  * If OS lacks atomic directory replace, implement file-by-file atomic renames and a manifest-based finalization.

### Permissions & Ownership

* Preserve file modes from `src` for assets where relevant.
* Allow `umask` or explicit permission config.
* For web-hosting, ensure directories are `0755` and files `0644` by default (configurable).

---

## Manifest Format & Management

`manifest.json` in `cache_dir` is the authoritative record of what the build produced and what the cache contains.

### Example schema (JSON)

```json
{
  "schema_version": 1,
  "build_time": "2025-10-28T12:34:56Z",
  "ssg_version": "3.0.0",
  "permalink_template_hash": "sha256:...",
  "template_hashes": { "default.html": "sha256:...", "python.html": "sha256:..." },
  "items": {
    "content/python/foo.md": {
      "out": "public/python/2025/10/28/foo/index.html",
      "url": "/python/2025/10/28/foo/",
      "cache_key": "sha256:...",
      "processor": "markdown_v1",
      "templates_used": ["templates/python.html","templates/_base.html"]
    },
    "index:page:1": {
      "out": "public/index.html",
      "url": "/",
      "cache_key": "sha256:..."
    }
  }
}
```

### Manifest Atomicity

* Write new manifest to a temp file, fsync, then `os.replace` over old manifest to ensure atomic update.
* The manifest includes `template_hashes` and `permalink_template_hash` used for invalidation decisions.

---

## CacheManager Integration (Write + Marking Processed)

WriteStage interacts with `CacheManager` to persist new cache entries and support selective rebuilds.

### Required CacheManager API (refined)

```python
class CacheManager(ABC):
    def begin_transaction(self) -> None
    def mark_processed(self, src: str, cache_key: str, metadata: dict) -> None
    def remove_items(self, keys: Iterable[str]) -> None
    def get_items_using_template(self, template_path: Path) -> List[str]
    def save_manifest(self, manifest: dict) -> None
    def commit_transaction(self) -> None
    def rollback_transaction(self) -> None
```

### Transaction semantics

* Start a DB transaction before writing cache updates.
* Only commit cache changes if the entire write flow (file writes + manifest update + swap) succeeded.
* On failure, rollback to avoid inconsistent cache pointing to uncommitted output.

---

## Cleanup & Orphans Removal

After publishing new output and updating the manifest, remove outputs present in the old manifest but absent in the new one.

### Safe cleanup procedure

1. Compute `old_set = set(old_manifest['items'].values().map(item['out']))`
2. Compute `new_set = set(new_manifest['items']... )`
3. `orphans = old_set - new_set`
4. For each orphan:

   * Verify it is inside `output_dir` and not a symlink pointing outside.
   * Remove file or directory (if empty). If directory not empty, either:

     * Remove recursively if all children are orphaned, or
     * Leave and log (safer), or
     * Warn and require manual intervention (configurable strictness).
5. Optionally keep a short-term backup of deleted files for fast rollback (`--keep-old-output-days`).

**Important:** Never delete files outside `output_dir`. Always confirm paths are under output root.

---

## Failure Modes & Recovery

### 1) Failure during writing to `output_dir_tmp`

* If writing a file fails:

  * Log error with `src`, `dest`, underlying exception.
  * Abort write, delete `output_dir_tmp` (best-effort).
  * Do **not** touch existing `output_dir`.
  * Return exit code `2` (commit/write error).
  * No cache/manifest updates applied.

### 2) Failure during renaming/swap

* If rename of `output_dir_tmp` to `output_dir` fails:

  * Attempt to roll back by deleting `output_dir_tmp`.
  * If `output_dir` still exists (old site intact), keep it unchanged and report error.
  * If `output_dir` was partially replaced (platform-specific), try to restore from `output_dir_old_<ts>` if available.
  * If no recovery possible, leave system in a safe but possibly inconsistent state and instruct manual restore from backup (log paths).

### 3) Failure during manifest write or cache transaction

* If manifest write fails after swap:

  * If manifest is required by downstream operations, attempt to restore old output (if old output was archived) or mark system as needing manual repair.
  * Prefer writing manifest into `cache_dir` first (temp + replace). Only after manifest is replaced do we consider the build fully successful.
  * Cache updates should be part of the same transaction as manifest save; if commit fails, rollback DB changes.

### 4) Partial cleanup failure

* If orphan deletion fails for specific files (permissions), log warnings and continue; do not revert successful swap. Provide a summary and suggestion to run `ssg clean` manually.

---

## Security & Safety Considerations

* **Path traversal protections:** Ensure `out` paths are normalized and resolved to be under `output_dir`. Reject any item with `out` path outside `output_dir`.
* **Symlink handling:** Do not follow symlinks outside site root when copying assets. For swapped output, ensure symlinks don’t point to sensitive locations.
* **File permission sandboxing:** Validate write permissions before swap. If output_dir is owned by root or different user, fail with clear message.
* **User-supplied templates:** Rendering sandbox: avoid executing arbitrary Python. Use template engine sandboxing features (Jinja2 has sandbox extension) or document security expectations.

---

## Concurrency / Parallel Writes

* Optionally use worker pool to write files in parallel to `output_dir_tmp` to speed up IO-bound operations.
* Keep writes idempotent and independent; protect OutputWriter with thread safety if needed.
* Limit concurrency to avoid overwhelming disk I/O (config `write_concurrency`).

---

## Tests for WriteStage

1. **Cold atomic swap**

   * Build to `output_dir_tmp`, swap, verify `output_dir` now contains exact expected files and old output removed.

2. **Low-disk manifest mode**

   * Use manifest-driven overwrite, simulate mid-write failure, ensure old files remain intact, and manifest not updated.

3. **Rollback on write failure**

   * Simulate permission error on one output file; assert swap not performed and `output_dir` unchanged.

4. **Orphan removal**

   * With previous manifest containing extra files, run build and confirm orphans removed (or flagged when not deletable).

5. **Concurrent write behavior**

   * Stress test with high `write_concurrency`, ensure no corrupt files and manifest consistent.

6. **Security tests**

   * Attempt to generate `out` paths outside `output_dir`; assert validation rejects them.

---

## Example Pseudocode — WriteStage (Atomic Swap)

```python
def write_stage(built_items, config, cache_manager, output_writer, manifest_old):
    # preconditions: built_items are valid, errors checked
    tmp_dir = create_temp_output_dir(config.output_dir)
    try:
        for item in built_items:
            dest = tmp_dir.joinpath(item.out.relative_to(config.output_dir))
            output_writer.ensure_directory(dest.parent)
            if item.kind == 'asset':
                output_writer.copy_file(item.src, dest, preserve_mtime=True)
            else:  # content/index
                output_writer.write_text(dest, item.html, encoding='utf-8')
            cache_manager.mark_processed(item.src, item.cache_key, item.metadata)
        # write manifest to cache (temp then replace)
        new_manifest = build_manifest(built_items, config)
        cache_manager.save_manifest_atomic(new_manifest)
        # atomic swap
        rotate_and_replace_dir(config.output_dir, tmp_dir)
        # after-swap cleanup & orphan removal
        delete_orphans(manifest_old, new_manifest, output_writer)
        cache_manager.commit_transaction()
        return success_stats
    except Exception as e:
        cache_manager.rollback_transaction()
        safe_delete(tmp_dir)
        log.error("Write failed: %s", e)
        raise CommitError from e
```

---

## Integration Notes & Best Practices

* Prefer **Atomic Directory Swap** for reliability; provide `--low-disk` option to use manifest-driven mode.
* Keep manifest as source of truth; never delete files without consulting manifest diff.
* Provide a `--dry-run` build mode which performs BuildStage + creates `output_dir_tmp` but does not swap; useful for CI and testing.
* Provide a `--keep-old` flag to avoid deleting `output_dir_old_<ts>` for N builds (useful for quick rollback).
* Expose clear logs and build-report containing counts (written, skipped, orphans deleted, time spent).

---

## 1 — CLI: Commands & UX

Top-level entrypoint: `ssg`

Usage pattern:

```
ssg [global options] <command> [command options]
```

Global options:

* `--config PATH` (default `./config.toml`)
* `--env ENV` (`dev|prod`)
* `--log-level LEVEL`
* `--concurrency N`
* `--dry-run` (BuildStage only)
* `--low-disk` (use manifest-driven write mode)
* `--keep-old N` (keep N previous outputs)

Commands:

* `init [--template GROUP]` — scaffold site
* `build` — full build

  * `--full-validation` (forces extra file checks)
  * `--verbose`
  * `--watch` (future)
  * `--migrate-cache` (attempt safe migration)
* `clean [--output] [--cache]` — remove cache/output
* `serve [--port PORT]` — development server (serves `output_dir_tmp` or `output_dir` depending on mode)
* `status` — show manifest summary and last build stats

Exit codes:

* `0` success
* `1` validation/build errors (before write)
* `2` commit/write errors
* `3` config errors
* `4` filesystem/permission errors

CLI should:

* Produce machine-readable JSON with `--json` for CI
* Return human-friendly error messages and suggestions
* Support `--dry-run` to skip WriteStage but still create `manifest` preview

---

## 2 — Public API Interfaces (stable surface)

### Config dataclass (example)

```python
@dataclass
class Config:
    source_dir: Path
    content_dirs: List[Path]
    asset_dirs: List[Path]
    output_dir: Path
    cache_dir: Path = Path('.ssg_cache')
    template_dir: Path = Path('templates')
    content_extensions: List[str] = field(default_factory=lambda:['.md','.markdown'])
    blacklist: List[str] = field(default_factory=list)
    page_size: int = 10
    permalink_templates: Dict[str,str] = field(default_factory=dict)
    incremental: bool = True
    validation_mode: str = 'incremental'
    concurrency: int = 1
    slug_preserve_unicode: bool = False
    cache_schema_version: int = 1
```

### Processor base class

```python
class Processor(ABC):
    id: str  # e.g. "markdown_v1"

    def before_build(self, ctx: BuildContext) -> None: ...
    def build(self, item: BuildItem, services: Services) -> BuildItem: ...
    def before_write(self, ctx: BuildContext) -> None: ...
    def after_write(self, ctx: BuildContext) -> None: ...
    def can_handle(self, item: BuildItem) -> bool: ...
```

### CacheManager API

```python
class CacheManager(ABC):
    def needs_processing(self, src: Path, cache_key: str) -> bool: ...
    def load_metadata(self, src: Path) -> Optional[dict]: ...
    def mark_processed(self, src: Path, cache_key: str, metadata: dict) -> None: ...
    def get_items_using_template(self, template_path: Path) -> List[str]: ...
    def save_manifest_atomic(self, manifest: dict) -> None: ...
    def begin_transaction(self) -> None: ...
    def commit_transaction(self) -> None: ...
    def rollback_transaction(self) -> None: ...
```

### OutputWriter API


### TemplateRenderer API

```python
class TemplateRenderer(ABC):
    def load_templates(self, template_dir: Path) -> None: ...
    def render(self, template_name: str, ctx: dict) -> str: ...
    def get_template_hash(self, template_name: str) -> str: ...
    def get_templates_used(self) -> List[Path]: ...
```

### PermalinkGenerator API

```python
class PermalinkGenerator(ABC):
    def set_templates(self, templates: Dict[str,str]) -> None: ...
    def validate_template(self, name: str) -> None: ...
    def generate(self, metadata: dict) -> Tuple[str, Path]:  # returns (url, out_path)
```

### MetadataExtractor API

```python
class MetadataExtractor(ABC):
    def parse_frontmatter(self, raw: str) -> dict: ...
    def extract_from_file(self, src: Path, defaults: dict) -> dict: ...
    def generate_slug(self, text: str) -> str: ...
    def parse_date(self, value: Any) -> datetime: ...
```

---

## 3 — Testing Matrix (priority & examples)

### Unit tests (fast)

* PermalinkGenerator: placeholder parsing, formatting edge cases, invalid placeholders
* MetadataExtractor: frontmatter parsing (YAML/TOML), slug generation unicode edge-cases
* TemplateRenderer: rendering minimal template, `get_template_hash` includes partials
* CacheManager: migrate, mark_processed, needs_processing behavior with fake DB
* OutputWriter: atomic rename semantics (use tmp dir), file perms

### Integration tests (filesystem-level)

* Cold build (no cache): build small fixture site and assert file outputs match snapshot
* Incremental build: modify one file, run build again; assert only that item and affected indexes were rebuilt
* Template partial change: change a partial and assert only consumers rebuild
* Move file w/ frontmatter category: ensure URL stays same (Option 3 semantics)
* URL collision: two files that resolve to same URL → build fails with clear message

### E2E tests (CI)

* Large-ish site build (1000 posts) to validate performance and memory
* Low-disk mode (manifest-driven) — simulate small disk and ensure correctness
* Concurrent builds: run two builds concurrently (with different output dirs) to ensure cache isolation

### Security tests

* Attempt outputs with out-of-root `out` → assert validation failure
* Template sandboxing: inject template code attempting to access os.env or filesystem (ensure sandboxing or doc warning)

---

## 4 — Example Implementation Skeletons (Python pseudo code)

### BuildPipeline skeleton

```python
class BuildPipeline:
    def __init__(self, config: Config, services: Services, processors: List[Processor]):
        self.config = config
        self.services = services
        self.processors = processors

    def run(self, dry_run=False):
        scan_ctx = ScanStage(self.config).run()
        built_items, errors = BuildStage(self.config, self.services, self.processors).run(scan_ctx)
        if errors:
            return BuildResult(success=False, errors=errors)
        if dry_run:
            return BuildResult(success=True, stats=...)
        WriteStage(self.config, self.services, self.processors).run(built_items)
        return BuildResult(success=True, stats=...)
```

### MarkdownContentProcessor sketch

```python
class MarkdownContentProcessor(Processor):
    id = "markdown_v1"

    def can_handle(self, item): return item.kind == 'content'

    def build(self, item, services):
        raw = services.file.read(item.src)
        front, body = services.metadata.parse_frontmatter(raw)
        metadata = services.metadata.extract_from_file(item, front)
        html_body = markdown_to_html(body, extensions=services.config.markdown_extensions)
        template = services.templates.resolve_template(metadata)
        ctx = {...}
        final_html = services.templates.render(template, ctx)
        item.html = final_html
        item.templates_used = services.templates.get_templates_used()
        item.cache_key = compute_cache_key(...)
        return item
```

---

## 5 — Migration Notes

* Provide `ssg migrate-cache --from-version X` that:

  * Backs up existing cache dir
  * Reads old schema (sqlite/JSON) and maps fields to new `manifest.json` structure
  * Recomputes template hashes if necessary
  * If migration fails, restore backup and notify user

* Provide `ssg import-old-config` helper to migrate old config keys to the new dataclass format.

* Document manual steps for major breaking changes in `CHANGELOG.md`.

---

## 6 — Performance Targets & Benchmarks

These are target goals to aim for in implementations (measured on a decent dev machine; tune with concurrency):

* **Cold build** (1000 posts, 10KB each): < 90s (single-threaded)
* **Incremental build** (1000 posts, 1 changed): < 2s (hashing + 1 render + write)
* **Memory**: ~50–200MB depending on HTML size for 1000 posts; allow streaming option for lower memory
* **Template partial change**: rebuild only affected items; goal rebuild time < 10s for 10 affected pages

Document performance caveats and configuration knobs (concurrency, streaming, low-disk mode).

---

## 7 — Implementation Checklist (prioritized)

**Phase 0 — Foundation**

1. Implement Config dataclass + TOML loader + validator
2. Implement ScanStage (deterministic discovery)
3. Implement basic OutputWriter (local FS) with atomic file write helper
4. Implement PermalinkGenerator + basic tests
5. Implement simple CacheManager (JSON manifest-backed) for MVP

**Phase 1 — Core pipeline**
6. Implement Processor interface + MarkdownContentProcessor (M1) + CopyProcessor
7. Implement TemplateRenderer (Jinja2) with `get_template_hash` and `get_templates_used`
8. Implement BuildStage with deterministic cache key computation
9. Implement WriteStage using Atomic Directory Swap
10. Implement IndexGenerator + pagination templates

**Phase 2 — Robustness**
11. Add CacheManager DB implementation (sqlite + indices)
12. Add transaction support & tests
13. Implement `--low-disk` manifest-driven write mode
14. Add template partial dependency mapping & selective rebuilds
15. Add full-validation mode & file permission checks

**Phase 3 — Usability**
16. CLI commands + JSON output
17. `ssg init` scaffolding
18. Logging & progress reporting
19. Unit / integration tests suite
20. Documentation & migration tools

---

## 8 — Appendix: Common Implementation Pitfalls & Mitigations

* **Double-rendering** — ensure Markdown → HTML happens only in BuildStage (M1) and processors do not write files.
* **Stale cache on moves** — include resolved metadata parts (slug, category) in cache key per Option 3.
* **Partial write visibility** — use atomic swap or atomic file rename to avoid serving partial content.
* **Template partial dependency misses** — recursively compute template hash.
* **URL collisions with indexes** — include index virtual URLs into collision detection.

---


