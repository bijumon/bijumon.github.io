# SSGv3 Design - Core Specification

## Architecture Overview

SSGv3 is a static site generator built on a **three-stage pipeline** where each stage has exclusive responsibilities:

```
SCAN → BUILD → WRITE
```

**Core principle**: All validation and transformation happens in memory during BUILD. WRITE is a pure commit operation that either completes fully or leaves the previous output untouched.

### Stage Boundaries

| Stage | File Reads | Transformations | File Writes | Failures Allowed |
|-------|-----------|-----------------|-------------|------------------|
| SCAN  | Metadata only (stat) | None | None | Yes (abort before BUILD) |
| BUILD | Content (changed files only) | Markdown→HTML, Template rendering | None | Yes (abort before WRITE) |
| WRITE | None | None | All outputs | No (atomic commit) |

**Guarantee**: If BUILD completes without errors, WRITE will succeed or leave the system in the previous consistent state.

---

## Core Data Model

### BuildItem

Every discovered file becomes a BuildItem. After processing, it may become:

- **ContentItem**: Markdown file that generates HTML
- **AssetItem**: File copied byte-for-byte (CSS, images, etc.)
- **IndexItem**: Virtual item for paginated index pages

Each BuildItem contains:

- **src**: Original source file path (null for virtual items)
- **out**: Final output path (resolved during BUILD)
- **url**: Site-relative URL (e.g., `/python/2025/intro/`)
- **kind**: `content | asset | index`
- **state**: `SCANNED | BUILT | WRITTEN`
- **metadata**: Resolved metadata dictionary
- **cache_key**: SHA256 hash identifying this item's dependencies
- **html**: Rendered HTML (content and index items only)

---

## Stage 1: SCAN

### Purpose

Fast discovery of all source files with minimal I/O. Produces a deterministic list of BuildItems with initial metadata.

### Inputs

- Project directory structure
- Content directory (e.g., `content/`)
- Asset directory (e.g., `assets/`)
- Blacklist patterns (e.g., `['.git', '_drafts']`)

### Process

1. **Directory Walking**: Traverse content and asset directories using filesystem scanning
2. **Filtering**: Skip blacklisted paths, hidden directories (`.git`, `.cache`), and output/cache directories
3. **Classification**: Determine item kind based on file extension:
   - `.md`, `.markdown` → content
   - Everything else → asset
4. **Initial Metadata**: Extract from file path structure:
   - `initial_slug`: Filename without extension
   - `initial_category`: Immediate parent directory name (empty if top-level)
   - `path_rel`: Path relative to content/asset root
5. **File Stats**: Capture modification time and size (for change detection)
6. **Ordering**: Sort items by relative path for deterministic processing

### Outputs

List of `BuildItem(state=SCANNED)` with minimal metadata. No file contents read, no transformations performed.

### Example

```
Input structure:
  content/python/intro.md
  content/rust/ownership.md
  assets/style.css

Output items:
  BuildItem(src=content/python/intro.md, kind=content, 
            initial_slug=intro, initial_category=python)
  BuildItem(src=content/rust/ownership.md, kind=content,
            initial_slug=ownership, initial_category=rust)
  BuildItem(src=assets/style.css, kind=asset,
            initial_slug=style, initial_category='')
```

---

## Stage 2: BUILD

### Purpose

Transform source files into renderable outputs, resolve all metadata, detect collisions, and prepare everything for atomic write. All operations happen in memory.

### Two-Phase Process

BUILD operates in two distinct phases to resolve circular dependencies:

**Phase 1: Content Processing**
- Process all content and asset items
- Assign final cache_key to each item
- Items are now ready for indexing

**Phase 2: Index Generation**
- Create virtual IndexItems for pagination
- Use cache_keys from Phase 1 in index cache computation
- Detect URL collisions across all items

### Phase 1: Content Processing

For each BuildItem from SCAN:

#### 1. Metadata Resolution

Merge metadata from three sources in order of precedence (later sources override earlier):

**System Defaults**:
- `slug`: filename without extension
- `category`: parent directory name
- `date`: file modification time

**Path-Derived** (only if not in frontmatter):
- Category from directory structure
- Date from filename patterns like `YYYY-MM-DD-title.md`

**Frontmatter** (always wins):
- Any explicitly set field overrides all others
- Parsed from YAML block at file start
- Example: `category: tutorials` overrides directory structure

**Key behavior**: Files can move between directories without URL changes if frontmatter specifies category. Without frontmatter, URL follows directory structure.

#### 2. Slug Normalization

Convert title/filename into URL-safe slug:

- Convert to lowercase
- Transliterate Unicode to ASCII (ö → o, é → e)
- Remove all punctuation except hyphens
- Replace whitespace sequences with single hyphen
- Strip leading/trailing hyphens

Result: `"My Cool Post!"` → `"my-cool-post"`

#### 3. Cache Key Computation

Compute a deterministic SHA256 hash that captures all inputs affecting the rendered output:

```
Input object (deterministically serialized to JSON):
{
  "content_hash": SHA256(file_bytes),
  "metadata": {
    "slug": resolved_slug,
    "category": resolved_category,
    "date_iso": resolved_date_in_ISO_format
  },
  "selected_template": template_name,
  "template_hash": hash_of_template_and_all_its_includes,
  "permalink_format": "{category}/{year}/{month}/{slug}/",
  "schema_version": 1
}

cache_key = SHA256(JSON.dumps(input_object, sorted_keys))
```

**Critical**: Template hash must include all partials/includes transitively (see Template Dependency Tracking section).

#### 4. Cache Consultation

Check if this item needs processing:

- **Cache hit** (cache_key matches stored key):
  - Load pre-rendered HTML from cache
  - Load resolved metadata
  - Skip to next item

- **Cache miss** (no entry or key changed):
  - Read file contents
  - Parse frontmatter
  - Transform Markdown to HTML
  - Render through template
  - Store result in memory for WRITE

#### 5. Template Selection

Choose template using first-match algorithm:

1. If frontmatter contains `template: X` → use `templates/X.html`
2. Else if category-specific template exists → use `templates/{category}.html`
3. Else use `templates/default.html` (required)

**Error if**: Selected template file doesn't exist.

#### 6. Content Transformation

**For content items** (cache miss only):

1. Read file as UTF-8 (fail if invalid encoding)
2. Split frontmatter (YAML between `---` markers) from body
3. Parse Markdown body to HTML (single pass, with configured extensions)
4. Assemble template context:
   - `content`: HTML body
   - `metadata`: All resolved metadata
   - `site`: Global site configuration
5. Render final HTML through selected template
6. Track which templates were used (for invalidation)

**For asset items**:
- No transformation
- Cache key based only on file hash and output path

#### 7. Permalink Generation

Apply permalink template to resolved metadata:

**Template format**: `{category}/{year:04d}/{month:02d}/{slug}/`

**Supported placeholders**:
- `{category}`: Category string
- `{year}`, `{month}`, `{day}`: Date components with optional formatting
- `{slug}`: URL-safe slug

**Example**:
```
Metadata: {category: "python", date: "2025-10-28", slug: "intro"}
Template: "{category}/{year}/{month}/{slug}/"
Result URL: "/python/2025/10/intro/"
Output path: "public/python/2025/10/intro/index.html"
```

**URL Normalization Rules**:
- All URLs end with `/` (trailing slash required)
- All URLs are lowercase
- Multiple slashes collapsed to single slash
- Leading slash always present

#### 8. Assign Final Paths

For each item:
- Set `item.url` to normalized permalink
- Set `item.out` to filesystem output path (URL + `index.html`)
- Set `item.cache_key` to computed hash
- Set `item.state = BUILT`

### Phase 2: Index Generation

After all content items have cache_keys assigned:

#### 1. Collect Items for Indexing

**Main index**: All content items, sorted by date descending
**Category indexes**: Items grouped by category, sorted by date descending

#### 2. Paginate Item Lists

Split sorted items into pages using configured page size (e.g., 10 posts per page).

**Page URLs**:
```
Main index:
  Page 1: /index.html
  Page 2: /page/2/index.html
  Page 3: /page/3/index.html

Category index (e.g., python):
  Page 1: /python/index.html
  Page 2: /python/page/2/index.html
```

#### 3. Compute Index Cache Keys

For each index page, compute cache key capturing:

```
{
  "index_type": "main" or "category:python",
  "page_number": 2,
  "template_hash": hash_of_index_template,
  "pagination_context": {
    "total_items": 47,
    "total_pages": 5,
    "items_per_page": 10
  },
  "items_on_page": [
    {
      "cache_key": item.cache_key,
      "url": item.url,
      "date_iso": item.metadata.date_iso
    }
    for each item on this page (sorted order)
  ]
}
```

**Key insight**: This captures both membership and ordering. Any change to constituent items or pagination boundaries invalidates the index page.

#### 4. Check Index Cache

For each index page:

- **Cache hit**: Load pre-rendered HTML
- **Cache miss**: Render index template with:
  - Current page items
  - Pagination metadata (current page, total pages, prev/next URLs)
  - Category information (for category indexes)

#### 5. Create IndexItems

Construct virtual BuildItems:
- `kind = index`
- `src = null` (virtual item)
- `url` and `out` set to index page paths
- `html` contains rendered or cached HTML
- `state = BUILT`

Add IndexItems to the main items list.

### Collision Detection

After both phases complete:

1. Build URL map: `{url: [items_with_that_url]}`
2. Normalize all URLs before mapping
3. Identify collisions: any URL with multiple source items
4. For each collision:
   - Create detailed error with all source paths
   - Suggest resolution (change slug in frontmatter, change category, adjust permalink template)
5. If any collisions found, abort before WRITE

**Special cases checked**:
- Content item URL matching index URL
- Asset filename matching generated content URL
- Multiple content items with same slug in same category

### Error Collection

BUILD accumulates all errors without stopping:

- Frontmatter parse failures
- Invalid date formats
- Missing required templates
- URL collisions
- Encoding errors

At end of BUILD, if any errors exist, return error list and abort. No partial builds.

### BUILD Success Criteria

BUILD phase succeeds only when:
- All items processed without errors
- All cache keys computed
- All URLs resolved and collision-free
- All HTML rendered (or loaded from cache)
- No missing templates
- All items in `state=BUILT`

---

## Template Dependency Tracking

### Problem

Template changes must invalidate all items that use them, including transitive dependencies through partials/includes.

### Template Hash Computation

When templates are loaded:

1. **Build dependency graph**:
   - Parse each template for include/import statements
   - Build map: `{template_name: [included_template_names]}`

2. **Detect cycles**:
   - Walk dependency graph with depth-first search
   - Track visiting vs. visited nodes
   - If cycle detected: **reject template set with error**
   - Example error: "Circular template dependency: base.html → header.html → base.html"

3. **Compute hashes bottom-up**:
   - Start with leaf templates (no includes)
   - For each template with includes:
     ```
     template_hash = SHA256(
       template_file_content +
       sorted_list_of_included_template_hashes
     )
     ```
   - Store computed hash for reuse

4. **Cache hash results**: Template hashes are computed once at template load and reused for all items.

### Invalidation on Template Change

When a template file changes:

1. Recompute its hash (and hashes of templates that include it)
2. Query cache for items that used that template
3. Mark those items as needing rebuild
4. During BUILD, these items get cache misses and reprocess

**Note**: Template hash is included in item cache_key, so any template change naturally invalidates dependent items.

---

## Stage 3: WRITE

### Purpose

Atomically commit all built outputs to disk. Either complete successfully or leave previous output unchanged.

### Atomic Commit Strategy

SSGv3 uses **symlink-based atomic swap** for true atomicity:

#### Output Directory Structure

```
project/
  public@ -> output_20251028_143022/   # symlink to current build
  output_20251028_143022/              # actual output directory (timestamped)
  output_20251028_120000/              # previous build (kept for rollback)
```

The canonical `public/` path is always a symlink, never a real directory.

#### Write Process

1. **Create timestamped directory**: `output_YYYYMMDD_HHMMSS/`

2. **Write all outputs**:
   - For each BUILT item:
     - Create parent directories as needed
     - Write file contents
     - For assets: copy bytes preserving modification time
     - For content/index: write HTML as UTF-8 text
   - All writes to temporary directory, not live output

3. **Fsync all files**: Ensure writes are committed to disk

4. **Write manifest**:
   - Create `cache/manifest.json.new` with:
     - Build timestamp
     - List of all items with their cache_keys and output paths
     - Template hashes used
   - Fsync manifest file
   - Atomically rename `manifest.json.new` → `manifest.json`
   - **This is the commit point for cache**

5. **Update symlink atomically**:
   ```
   ln -sf output_20251028_143022 public.tmp
   mv -T public.tmp public
   ```
   - The `mv` of symlink is atomic on POSIX systems
   - Between creation of `.tmp` and final `mv`, live site remains on old build
   - The `mv` operation switches the site instantly

6. **Cleanup old outputs**:
   - Keep N most recent output directories (configurable, default 2)
   - Delete older timestamped directories
   - This provides instant rollback capability

### Success and Failure

**Success criteria**:
- All files written to timestamped directory
- Manifest committed
- Symlink updated
- Old outputs cleaned (if cleanup enabled)

**On failure during file writes**:
- Delete incomplete timestamped directory
- Leave `public` symlink unchanged (still points to previous good build)
- No manifest update
- Report error and exit with code 2

**On failure during symlink update** (rare):
- Attempt to delete timestamped directory
- Leave system with previous build active
- Report error with manual recovery steps
- Exit with code 2

**Guarantee**: Users never see partially-written output. Site is either old version or new version, never mixed.

### Non-Symlink Fallback

On systems without symlink support (Windows without dev mode):

1. Write to `output.tmp/` directory
2. After all writes succeed and manifest committed:
   - Rename `output/` → `output.old/` (if exists)
   - Rename `output.tmp/` → `output/`
   - Delete `output.old/`

**Limitation**: Small time window where `output/` doesn't exist (between renames). Document this as degraded atomicity mode.

### Orphan Cleanup

After successful symlink update:

1. Load previous manifest
2. Compare with new manifest
3. Identify files in old manifest but not in new manifest (orphans)
4. For each orphan path:
   - Verify it's inside previous output directory
   - Delete file
   - Delete parent directories if empty

**Safety**: Only delete from old timestamped directories, never from current output. This is safe because old directories are not served.

---

## Cache Management

### Cache Structure

Cache stored in `.ssg_cache/` directory:

- `manifest.json`: Authoritative record of last successful build
- `db.sqlite`: Item metadata and dependencies (optional, for advanced queries)

### Manifest Format

```json
{
  "schema_version": 1,
  "build_timestamp": "2025-10-28T14:30:22Z",
  "ssg_version": "3.0.0",
  "template_hashes": {
    "default.html": "sha256:abc...",
    "python.html": "sha256:def..."
  },
  "permalink_template": "{category}/{year}/{month}/{slug}/",
  "items": {
    "content/python/intro.md": {
      "cache_key": "sha256:123...",
      "url": "/python/2025/10/intro/",
      "out": "output_20251028_143022/python/2025/10/intro/index.html",
      "templates_used": ["default.html"]
    },
    ...
  }
}
```

### Cache Operations

**During BUILD**:
- Read manifest to check cache_keys
- On cache hit: load cached HTML and metadata
- On cache miss: mark item for processing

**During WRITE**:
- After all files written
- Before symlink update
- Write new manifest atomically
- Manifest commit makes cache changes durable

**Cache invalidation triggers**:
- Source file content changed (content_hash differs)
- Template changed (template_hash differs)
- Metadata changed (different date/slug/category in frontmatter)
- Permalink format changed
- Dependencies changed (for indexes: constituent items changed)

### Cold Build vs. Incremental Build

**Cold build** (no cache):
- Process all items
- Generate all outputs
- Create initial manifest

**Incremental build** (cache exists):
- SCAN: detect all files as before
- BUILD Phase 1:
  - Compute cache_key for each item
  - Compare with manifest
  - Process only items with changed keys
  - Load cached HTML for unchanged items
- BUILD Phase 2:
  - Check index cache keys
  - Rebuild only indexes whose constituent items changed
- WRITE: Commit new manifest and swap outputs

**Performance target**: For 1000-post site with 1 file changed, incremental build should complete in under 5 seconds.

---

## Metadata Precedence Model

### Three Sources, Clear Rules

Metadata comes from three sources with strict precedence:

1. **System Defaults** (lowest priority)
2. **Path-Derived** (medium priority)
3. **Frontmatter** (highest priority)

### Example Walkthrough

File: `content/tutorials/python/intro.md`

**System defaults provide**:
- `slug: "intro"` (from filename)
- `category: "python"` (from parent directory)
- `date: 2025-10-28` (from file mtime)

**Frontmatter overrides**:
```yaml
---
title: Introduction to Python
category: programming-basics
date: 2024-06-15
---
```

**Final resolved metadata**:
- `slug: "intro"` (default, not overridden)
- `category: "programming-basics"` (frontmatter wins)
- `date: 2024-06-15` (frontmatter wins)
- `title: "Introduction to Python"` (from frontmatter)

**Resulting URL**: `/programming-basics/2024/06/intro/`

### Stability Guarantees

**With frontmatter category**:
- File can move to any directory
- URL remains stable (frontmatter category used)
- Useful for reorganizing source without breaking links

**Without frontmatter category**:
- URL tracks directory structure
- Moving file changes URL
- Useful for organizing by category via folders

**User choice**: Explicit frontmatter for stable URLs, directory structure for convenience.

---

## Key Design Decisions

### 1. Why Three Stages?

**Separation of concerns**:
- SCAN: Pure discovery, no side effects, fast
- BUILD: All computation and validation, memory-only
- WRITE: Pure commit, no decisions

**Benefits**:
- Easy to test each stage in isolation
- Clear failure boundaries
- Can abort before any writes
- Can preview build output before committing

### 2. Why Symlink-Based Atomic Swap?

**Problem**: Directory rename atomicity varies by filesystem and platform.

**Solution**: Symlink update is atomic on all POSIX systems (single syscall).

**Tradeoff**: Requires symlink support, but this is standard on Linux/macOS and modern Windows.

**Result**: True atomic site publish with zero-downtime deployments.

### 3. Why Two-Phase BUILD?

**Problem**: Index cache keys need content item cache keys, but indexes are also items.

**Solution**: Process content first (compute cache keys), then generate indexes (using those keys).

**Benefit**: Clear dependency ordering, no circular references.

### 4. Why Template Dependency Tracking?

**Problem**: Changing a shared partial should rebuild all pages that use it.

**Without tracking**: Must rebuild entire site on any template change.

**With tracking**: Rebuild only affected pages, preserving incremental build performance.

**Implementation cost**: Parse templates once at load, compute hashes with includes. Worth the complexity for speed.

### 5. Why Reject Circular Template Dependencies?

**Alternative**: Allow cycles, break arbitrarily during hash computation.

**Problem**: Non-deterministic behavior, unpredictable cache invalidation.

**Decision**: Reject cycles explicitly. Templates should compose in directed acyclic graph. Cycles indicate design error.

**Benefit**: Clear, predictable behavior. Easy to debug.

### 6. Why Include Pagination Context in Index Cache?

**Problem**: Adding one post can shift items between pages without changing the items on a specific page.

**Example**: Post #11 appears on page 2. Add new post at top. Post #11 now on page 2 (but it's the 12th post). Page 2 content unchanged but pagination controls need updating.

**Solution**: Include total counts and page boundaries in cache key. Any change to pagination structure invalidates all affected index pages.

**Tradeoff**: Adding one post invalidates multiple index pages. Acceptable because indexes are cheap to render compared to content.

---

## Error Handling Philosophy

### Fail Fast, Fail Explicitly

- Detect errors as early as possible
- Never write partial output
- Accumulate all errors before reporting
- Provide actionable error messages with suggestions

### Error Categories

**Configuration errors** (fail in SCAN):
- Invalid config file
- Missing required directories
- Malformed blacklist patterns

**Content errors** (fail in BUILD Phase 1):
- Invalid frontmatter YAML
- Unparseable dates
- Missing required metadata
- Invalid UTF-8 encoding

**Template errors** (fail in BUILD Phase 1):
- Missing template files
- Circular template dependencies
- Template syntax errors

**Collision errors** (fail in BUILD Phase 2):
- Multiple items generating same URL
- Index URL conflicting with content URL

**Write errors** (fail in WRITE):
- Disk full
- Permission denied
- Filesystem errors

### Recovery Patterns

**Before WRITE**: No recovery needed, just abort. Previous build still intact.

**During WRITE**: Partial writes cleaned up, symlink left pointing to previous build. User can fix issue and retry.

**After WRITE**: Success. Any issues in cleanup (old output deletion) logged but don't cause failure.

---

## Performance Model

### Bottlenecks and Optimizations

**SCAN**: I/O bound (filesystem traversal)
- **Optimization**: Filter early, prune ignored directories immediately
- **Target**: 10,000 files scanned in <2 seconds

**BUILD Phase 1**: CPU bound (Markdown parsing, template rendering)
- **Optimization**: Cache aggressively, process only changed items
- **Target**: 1 changed file in 1000-file site processes in <1 second

**BUILD Phase 2**: Memory bound (holding all items for indexing)
- **Optimization**: None needed for reasonable site sizes
- **Target**: Support sites with 10,000+ posts in <2GB memory

**WRITE**: I/O bound (writing files)
- **Optimization**: Batch directory creation, optional parallel writes
- **Target**: Write 1000 files in <3 seconds on SSD

### Scaling Characteristics

**Cold build**: O(n) in number of source files
**Incremental build**: O(m + log n) where m = changed files, n = total files
**Index rebuild**: O(k) where k = number of posts on changed index pages
**Memory usage**: O(n) where n = number of posts (holds HTML in memory)

### Practical Limits

- **Recommended**: Up to 5,000 posts, typical site
- **Tested**: Up to 10,000 posts
- **Theoretical**: Limited by available memory (roughly 5MB per 1000 posts for HTML storage)

---

## Summary of Core Concepts

1. **Three-Stage Pipeline**: Clear boundaries prevent partial builds
2. **Two-Phase BUILD**: Content first, then indexes (resolves dependencies)
3. **Cache Keys**: Deterministic hashes capture all dependencies
4. **Metadata Precedence**: System < Path < Frontmatter (users control URL stability)
5. **Template Tracking**: Transitive hash includes all partials, enables selective rebuilds
6. **Symlink Atomicity**: True atomic publish with rollback capability
7. **URL Normalization**: Consistent collision detection
8. **Fail-Before-Write**: All validation in BUILD, WRITE never fails
9. **Collision Detection**: Explicit checks prevent silent overwrites
10. **Incremental Correctness**: Cache invalidation based on complete dependency graph

These concepts compose to create a static site generator that is fast, correct, and predictable.