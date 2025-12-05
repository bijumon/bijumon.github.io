---
description: |
  This is a longer description.
  It has multiple lines.
  Line breaks are preserved as-is.
---

# SSGv3 Implementation Checklist - Test-First Approach

### Testing Strategy
- **Unit tests**: Test each component in isolation with mocks
- **Integration tests**: Test stage interactions with real file fixtures
- **E2E tests**: Full pipeline runs on sample sites
- **Property tests**: Use hypothesis for cache key determinism, URL normalization idempotence

### Test Data Principles
- Use realistic content (actual markdown with frontmatter)
- Cover boundary conditions (empty files, missing fields)
- Include unicode in slugs and content
- Test with various date formats and timezones
- Include invalid inputs to verify error handling

## Phase 1: Foundation - Data Structures & Models

### Core Models
- [ ] Write test: BuildItem creation with minimal fields
- [ ] Write test: BuildItem state transitions (SCANNED → BUILT → WRITTEN)
- [ ] Write test: BuildItem.to_dict() serialization
- [ ] Write test: BuildItem.from_dict() deserialization
- [ ] Implement BuildItem base class
- [ ] Write test: ContentItem with templates_used list
- [ ] Write test: AssetItem with preserve_mtime flag
- [ ] Write test: IndexItem with pagination fields
- [ ] Implement ContentItem, AssetItem, IndexItem subclasses

### Error Models
- [ ] Write test: SSGError with message and suggestion
- [ ] Write test: BuildError with code, src, message
- [ ] Write test: CollisionError with url and multiple sources
- [ ] Write test: TemplateError for missing template
- [ ] Implement error class hierarchy
- [ ] Write test: ErrorCollector accumulates multiple errors
- [ ] Write test: ErrorCollector.format_report() output
- [ ] Implement ErrorCollector class

### Configuration
- [ ] Write test: Config loads from TOML with all fields
- [ ] Write test: Config validates content_dir exists
- [ ] Write test: Config validates output_dir not inside content_dir
- [ ] Write test: Config validates permalink template syntax
- [ ] Write test: Config blacklist includes default patterns
- [ ] Implement Config dataclass with validation
- [ ] Write test: Config detects invalid page_size (< 1)
- [ ] Write test: Config normalizes paths to absolute

## Phase 2: Utilities Layer

### File Utilities
- [ ] Write test: FileUtils.read_file() handles UTF-8
- [ ] Write test: FileUtils.read_file() raises on invalid encoding
- [ ] Write test: FileUtils.stat_file() returns mtime and size
- [ ] Write test: FileUtils.is_ignored() matches patterns
- [ ] Implement FileUtils class
- [ ] Write test: FileUtils handles symlinks (don't follow by default)

### Date Parsing
- [ ] Write test: DateParser.parse() handles ISO format
- [ ] Write test: DateParser.parse() handles "YYYY-MM-DD" format
- [ ] Write test: DateParser.parse() handles human formats ("Jan 15, 2025")
- [ ] Write test: DateParser.to_iso() produces standard format
- [ ] Write test: DateParser.extract_from_filename() finds "YYYY-MM-DD-title.md"
- [ ] Implement DateParser class
- [ ] Write test: DateParser handles timezones consistently

### Path Resolution
- [ ] Write test: PathResolver.resolve() makes paths absolute
- [ ] Write test: PathResolver.make_relative() produces relative path
- [ ] Write test: PathResolver.is_within() detects containment
- [ ] Write test: PathResolver.is_within() rejects traversal attempts
- [ ] Implement PathResolver class

### Slug Generation
- [ ] Write test: SlugGenerator.generate() lowercases input
- [ ] Write test: SlugGenerator.generate() transliterates unicode (ö→o, é→e)
- [ ] Write test: SlugGenerator.generate() removes punctuation except hyphens
- [ ] Write test: SlugGenerator.generate() collapses whitespace to single hyphen
- [ ] Write test: SlugGenerator.generate() strips leading/trailing hyphens
- [ ] Implement SlugGenerator class
- [ ] Write test: SlugGenerator with preserve_unicode=True keeps diacritics

## Phase 3: Metadata System

### Metadata Extraction
- [ ] Write test: MetadataExtractor.parse_frontmatter() extracts YAML
- [ ] Write test: MetadataExtractor.parse_frontmatter() handles empty frontmatter
- [ ] Write test: MetadataExtractor.parse_frontmatter() raises on invalid YAML
- [ ] Write test: MetadataExtractor.get_system_defaults() uses filename for slug
- [ ] Write test: MetadataExtractor.get_system_defaults() uses mtime for date
- [ ] Write test: MetadataExtractor.get_path_derived() extracts category from parent
- [ ] Write test: MetadataExtractor.get_path_derived() handles top-level files
- [ ] Implement MetadataExtractor class
- [ ] Write test: MetadataExtractor.merge_metadata() respects precedence
- [ ] Write test: MetadataExtractor.extract() combines all three sources
- [ ] Write test: Frontmatter category overrides directory structure

## Phase 4: Template System

### Template Dependency Tracking
- [ ] Write test: TemplateDependencyTracker.build_graph() finds includes
- [ ] Write test: TemplateDependencyTracker.build_graph() parses Jinja2
- [ ] Write test: TemplateDependencyTracker.detect_cycles() finds A→B→A
- [ ] Write test: TemplateDependencyTracker.detect_cycles() handles self-reference
- [ ] Write test: TemplateDependencyTracker.detect_cycles() returns empty for DAG
- [ ] Implement TemplateDependencyTracker class
- [ ] Write test: TemplateDependencyTracker.compute_hash() includes content
- [ ] Write test: TemplateDependencyTracker.compute_hash() includes all includes transitively
- [ ] Write test: TemplateDependencyTracker.compute_hash() is deterministic
- [ ] Write test: TemplateDependencyTracker raises error on circular dependency

### Template Selection
- [ ] Write test: TemplateSelector.select() uses frontmatter template if present
- [ ] Write test: TemplateSelector.select() uses category template if exists
- [ ] Write test: TemplateSelector.select() falls back to default.html
- [ ] Write test: TemplateSelector.resolve_category_template() checks file exists
- [ ] Implement TemplateSelector class
- [ ] Write test: TemplateSelector raises error if default.html missing

### Template Rendering
- [ ] Write test: TemplateRenderer.load_templates() loads from directory
- [ ] Write test: TemplateRenderer.render() produces HTML
- [ ] Write test: TemplateRenderer.render() provides content in context
- [ ] Write test: TemplateRenderer.render() provides metadata in context
- [ ] Write test: TemplateRenderer.get_templates_used() tracks includes
- [ ] Implement TemplateRenderer with Jinja2
- [ ] Write test: TemplateRenderer handles missing template gracefully

## Phase 5: URL System

### URL Normalization
- [ ] Write test: URLNormalizer.normalize() adds trailing slash
- [ ] Write test: URLNormalizer.normalize() lowercases URL
- [ ] Write test: URLNormalizer.normalize() collapses multiple slashes
- [ ] Write test: URLNormalizer.normalize() ensures leading slash
- [ ] Implement URLNormalizer class
- [ ] Write test: URLNormalizer.normalize() is idempotent

### Permalink Generation
- [ ] Write test: PermalinkGenerator.parse_template() finds placeholders
- [ ] Write test: PermalinkGenerator.parse_template() handles format specs ({year:04d})
- [ ] Write test: PermalinkGenerator.apply_template() substitutes category
- [ ] Write test: PermalinkGenerator.apply_template() substitutes date parts
- [ ] Write test: PermalinkGenerator.apply_template() substitutes slug
- [ ] Implement PermalinkGenerator class
- [ ] Write test: PermalinkGenerator.generate() returns normalized URL
- [ ] Write test: PermalinkGenerator.resolve_output_path() appends index.html
- [ ] Write test: PermalinkGenerator validates template has required placeholders

### Collision Detection
- [ ] Write test: CollisionDetector.build_url_map() creates mapping
- [ ] Write test: CollisionDetector.find_collisions() detects duplicate URLs
- [ ] Write test: CollisionDetector.find_collisions() normalizes before comparing
- [ ] Write test: CollisionDetector.format_error() lists all source files
- [ ] Implement CollisionDetector class
- [ ] Write test: CollisionDetector.detect() handles empty list
- [ ] Write test: CollisionDetector catches index URL vs content URL collision

## Phase 6: Content Processing

### Markdown Transformation
- [ ] Write test: MarkdownTransformer.transform() converts headers
- [ ] Write test: MarkdownTransformer.transform() converts lists
- [ ] Write test: MarkdownTransformer.transform() handles code blocks
- [ ] Write test: MarkdownTransformer.configure_extensions() enables extensions
- [ ] Implement MarkdownTransformer class
- [ ] Write test: MarkdownTransformer with tables extension

### Content Processor
- [ ] Write test: ContentProcessor.read_file() loads content
- [ ] Write test: ContentProcessor.parse_content() splits frontmatter and body
- [ ] Write test: ContentProcessor.should_process() returns true for .md files
- [ ] Write test: ContentProcessor.process() combines all steps
- [ ] Implement ContentProcessor class
- [ ] Write test: ContentProcessor.process() sets templates_used
- [ ] Write test: ContentProcessor.process() resolves metadata
- [ ] Write test: ContentProcessor.process() renders through template

## Phase 7: Cache System

### Cache Key Computation
- [ ] Write test: CacheManager.compute_cache_key() includes content hash
- [ ] Write test: CacheManager.compute_cache_key() includes metadata
- [ ] Write test: CacheManager.compute_cache_key() includes template hash
- [ ] Write test: CacheManager.compute_cache_key() includes permalink template
- [ ] Write test: CacheManager.compute_cache_key() is deterministic
- [ ] Write test: CacheManager.compute_cache_key() changes when content changes
- [ ] Implement CacheManager.compute_cache_key()

### Cache Operations
- [ ] Write test: CacheManager.needs_processing() returns true on cold start
- [ ] Write test: CacheManager.needs_processing() returns false on cache hit
- [ ] Write test: CacheManager.needs_processing() returns true when key differs
- [ ] Write test: CacheManager.load_cached() returns stored HTML
- [ ] Write test: CacheManager.mark_processed() stores cache entry
- [ ] Implement CacheManager class with in-memory storage
- [ ] Write test: CacheManager persists across instances

### Manifest Management
- [ ] Write test: ManifestManager.load() parses JSON manifest
- [ ] Write test: ManifestManager.load() returns None if missing
- [ ] Write test: ManifestManager.save_atomic() writes to temp then renames
- [ ] Write test: ManifestManager.save_atomic() includes all item fields
- [ ] Write test: ManifestManager.compare() finds orphaned files
- [ ] Implement ManifestManager class
- [ ] Write test: ManifestManager handles corrupted manifest gracefully
- [ ] Write test: ManifestManager includes template hashes in manifest

## Phase 8: Index System

### Pagination
- [ ] Write test: Paginator.paginate() splits items by page_size
- [ ] Write test: Paginator.paginate() handles empty list
- [ ] Write test: Paginator.paginate() handles partial last page
- [ ] Write test: Paginator.get_page_url() generates /page/2/ format
- [ ] Write test: Paginator.get_page_url() generates /category/page/2/ for categories
- [ ] Write test: Paginator.get_page_url() generates /index.html for page 1
- [ ] Implement Paginator class

### Index Generation
- [ ] Write test: IndexGenerator.create_main_index() sorts by date desc
- [ ] Write test: IndexGenerator.create_main_index() paginates correctly
- [ ] Write test: IndexGenerator.create_category_indexes() groups by category
- [ ] Write test: IndexGenerator.compute_cache_key() includes items_on_page
- [ ] Write test: IndexGenerator.compute_cache_key() includes pagination context
- [ ] Write test: IndexGenerator.compute_cache_key() includes total_pages
- [ ] Implement IndexGenerator class
- [ ] Write test: IndexGenerator.should_rebuild() detects membership change
- [ ] Write test: IndexGenerator.should_rebuild() detects ordering change
- [ ] Write test: IndexGenerator.generate() creates IndexItems with correct URLs

## Phase 9: Stage 1 - SCAN

### Directory Walking
- [ ] Write test: ScanStage.walk_directory() finds all files
- [ ] Write test: ScanStage.walk_directory() skips blacklisted paths
- [ ] Write test: ScanStage.walk_directory() skips dot directories
- [ ] Write test: ScanStage.walk_directory() skips output directory
- [ ] Write test: ScanStage.should_ignore() matches blacklist patterns
- [ ] Implement ScanStage.walk_directory()

### File Classification
- [ ] Write test: ScanStage.classify_file() returns 'content' for .md
- [ ] Write test: ScanStage.classify_file() returns 'asset' for .css
- [ ] Write test: ScanStage.classify_file() returns 'asset' for images
- [ ] Implement ScanStage.classify_file()

### BuildItem Creation
- [ ] Write test: ScanStage.create_build_item() extracts initial_slug from filename
- [ ] Write test: ScanStage.create_build_item() extracts initial_category from parent
- [ ] Write test: ScanStage.create_build_item() handles top-level files
- [ ] Write test: ScanStage.create_build_item() captures file stats
- [ ] Implement ScanStage.create_build_item()

### Scan Integration
- [ ] Write test: ScanStage.run() returns sorted list of BuildItems
- [ ] Write test: ScanStage.run() marks all items as SCANNED
- [ ] Write test: ScanStage.run() on sample directory structure
- [ ] Implement ScanStage.run()
- [ ] Write test: ScanStage deterministic ordering (same input → same output)

## Phase 10: Stage 2 - BUILD Phase 1

### Content Item Processing
- [ ] Write test: BuildStage.process_content_item() reads file
- [ ] Write test: BuildStage.process_content_item() parses frontmatter
- [ ] Write test: BuildStage.process_content_item() merges metadata
- [ ] Write test: BuildStage.process_content_item() transforms markdown
- [ ] Write test: BuildStage.process_content_item() renders template
- [ ] Write test: BuildStage.process_content_item() computes cache_key
- [ ] Write test: BuildStage.process_content_item() generates permalink
- [ ] Implement BuildStage.process_content_item()

### Asset Item Processing
- [ ] Write test: BuildStage.process_asset_item() computes cache_key
- [ ] Write test: BuildStage.process_asset_item() generates output path
- [ ] Write test: BuildStage.process_asset_item() preserves relative path
- [ ] Implement BuildStage.process_asset_item()

### Cache Integration
- [ ] Write test: BuildStage.run_phase_one() checks cache before processing
- [ ] Write test: BuildStage.run_phase_one() loads cached HTML on hit
- [ ] Write test: BuildStage.run_phase_one() processes only cache misses
- [ ] Write test: BuildStage.run_phase_one() assigns cache_key to all items
- [ ] Implement BuildStage.run_phase_one()

### Error Collection
- [ ] Write test: BuildStage.collect_errors() accumulates parse errors
- [ ] Write test: BuildStage.collect_errors() accumulates template errors
- [ ] Write test: BuildStage.collect_errors() continues processing after errors
- [ ] Implement BuildStage.collect_errors()

## Phase 11: Stage 2 - BUILD Phase 2

### Index Creation
- [ ] Write test: BuildStage.run_phase_two() generates main index
- [ ] Write test: BuildStage.run_phase_two() generates category indexes
- [ ] Write test: BuildStage.run_phase_two() uses cache_keys from phase 1
- [ ] Write test: BuildStage.run_phase_two() computes index cache keys
- [ ] Write test: BuildStage.run_phase_two() checks index cache
- [ ] Write test: BuildStage.run_phase_two() renders index templates
- [ ] Implement BuildStage.run_phase_two()

### Collision Detection Integration
- [ ] Write test: BuildStage.detect_collisions() checks content items
- [ ] Write test: BuildStage.detect_collisions() checks index items
- [ ] Write test: BuildStage.detect_collisions() normalizes URLs first
- [ ] Write test: BuildStage.detect_collisions() returns CollisionErrors
- [ ] Implement BuildStage.detect_collisions()

### Build Integration
- [ ] Write test: BuildStage.run() executes phase 1 then phase 2
- [ ] Write test: BuildStage.run() detects collisions after phase 2
- [ ] Write test: BuildStage.run() returns errors if any found
- [ ] Write test: BuildStage.run() returns built items if no errors
- [ ] Implement BuildStage.run()
- [ ] Write test: BuildStage.run() on complete sample site

## Phase 12: Stage 3 - WRITE

### Output Writing
- [ ] Write test: OutputWriter.write_text() creates parent directories
- [ ] Write test: OutputWriter.write_text() writes UTF-8 content
- [ ] Write test: OutputWriter.copy_file() preserves mtime for assets
- [ ] Write test: OutputWriter.ensure_directory() creates nested paths
- [ ] Write test: OutputWriter.fsync() ensures durability
- [ ] Implement OutputWriter class

### Timestamped Directories
- [ ] Write test: WriteStage.create_timestamped_directory() uses YYYYMMDD_HHMMSS format
- [ ] Write test: WriteStage.create_timestamped_directory() creates directory
- [ ] Implement WriteStage.create_timestamped_directory()

### Atomic Swapping
- [ ] Write test: AtomicSwapper.verify_symlink_support() detects platform support
- [ ] Write test: AtomicSwapper.create_symlink() creates symlink
- [ ] Write test: AtomicSwapper.update_symlink_atomic() uses temp+rename pattern
- [ ] Write test: AtomicSwapper.swap() updates symlink atomically
- [ ] Implement AtomicSwapper class
- [ ] Write test: AtomicSwapper.swap() preserves old symlink target on failure

### Manifest Writing
- [ ] Write test: WriteStage.write_manifest() before symlink update
- [ ] Write test: WriteStage.write_manifest() includes all items
- [ ] Write test: WriteStage.write_manifest() includes template hashes
- [ ] Write test: WriteStage.write_manifest() uses atomic write
- [ ] Implement WriteStage.write_manifest()

### Cleanup
- [ ] Write test: OutputCleaner.find_orphans() compares manifests
- [ ] Write test: OutputCleaner.delete_old_outputs() keeps N recent
- [ ] Write test: OutputCleaner.keep_recent() sorts by timestamp
- [ ] Write test: OutputCleaner.cleanup() removes orphan files
- [ ] Implement OutputCleaner class
- [ ] Write test: OutputCleaner.cleanup() skips non-empty directories

### Write Integration
- [ ] Write test: WriteStage.run() creates timestamped directory
- [ ] Write test: WriteStage.run() writes all items to temp directory
- [ ] Write test: WriteStage.run() writes manifest
- [ ] Write test: WriteStage.run() updates symlink
- [ ] Write test: WriteStage.run() cleans old outputs
- [ ] Write test: WriteStage.run() on complete sample site
- [ ] Implement WriteStage.run()
- [ ] Write test: WriteStage.run() leaves previous output on failure

## Phase 13: Pipeline Integration

### Build Context
- [ ] Write test: BuildContext.add_item() stores item
- [ ] Write test: BuildContext.get_items() returns all items
- [ ] Write test: BuildContext filters items by state
- [ ] Implement BuildContext class

### Pipeline Orchestration
- [ ] Write test: Pipeline.run() executes SCAN stage
- [ ] Write test: Pipeline.run() executes BUILD stage
- [ ] Write test: Pipeline.run() executes WRITE stage
- [ ] Write test: Pipeline.run() aborts before WRITE if BUILD errors
- [ ] Write test: Pipeline.run() returns success on complete build
- [ ] Implement Pipeline.run()
- [ ] Write test: Pipeline.run_dry() skips WRITE stage
- [ ] Implement Pipeline.run_dry()

### End-to-End Tests
- [ ] Write test: Full pipeline on minimal site (1 page, 1 asset)
- [ ] Write test: Full pipeline on multi-category site
- [ ] Write test: Full pipeline with pagination (11+ posts)
- [ ] Write test: Incremental build (change 1 file, rebuild)
- [ ] Write test: Template change invalidation
- [ ] Write test: Collision detection prevents build
- [ ] Write test: Invalid frontmatter aborts before WRITE
- [ ] Write test: Second build uses cache (fast rebuild)

## Phase 14: Edge Cases & Robustness

### Encoding & Parsing
- [ ] Write test: ContentProcessor handles UTF-8 with BOM
- [ ] Write test: ContentProcessor handles mixed line endings
- [ ] Write test: MetadataExtractor handles TOML frontmatter
- [ ] Write test: MetadataExtractor handles missing frontmatter delimiter

### Template Edge Cases
- [ ] Write test: TemplateRenderer handles template with no includes
- [ ] Write test: TemplateRenderer handles deeply nested includes
- [ ] Write test: TemplateDependencyTracker handles partial with same name as template

### Permalink Edge Cases
- [ ] Write test: PermalinkGenerator handles missing date in metadata
- [ ] Write test: PermalinkGenerator handles empty category
- [ ] Write test: PermalinkGenerator handles special characters in slug
- [ ] Write test: PermalinkGenerator validates required placeholders present

### Cache Edge Cases
- [ ] Write test: CacheManager handles corrupted cache gracefully
- [ ] Write test: CacheManager handles schema version mismatch
- [ ] Write test: ManifestManager handles missing manifest file

### Write Edge Cases
- [ ] Write test: WriteStage handles disk full error
- [ ] Write test: WriteStage handles permission denied
- [ ] Write test: AtomicSwapper handles existing symlink
- [ ] Write test: AtomicSwapper rollback on failure
- [ ] Write test: OutputCleaner handles permission errors on delete

### Index Edge Cases
- [ ] Write test: IndexGenerator handles zero posts
- [ ] Write test: IndexGenerator handles exactly one page of posts
- [ ] Write test: Paginator handles page_size=1
- [ ] Write test: IndexGenerator handles category with one post

## Phase 15: Performance Validation

### Benchmarks
- [ ] Benchmark: SCAN 1000 files
- [ ] Benchmark: BUILD 1000 posts (cold)
- [ ] Benchmark: BUILD 1000 posts with 1 change (incremental)
- [ ] Benchmark: Template change affecting 100 posts
- [ ] Benchmark: WRITE 1000 files
- [ ] Benchmark: Full pipeline 1000 posts

### Memory Profiling
- [ ] Profile: Memory usage during BUILD with 1000 posts
- [ ] Profile: Memory usage during index generation
- [ ] Test: Verify no memory leaks across multiple builds

### Stress Tests
- [ ] Test: Build with 5000 posts
- [ ] Test: Site with 50 categories
- [ ] Test: Site with 1000 tags
- [ ] Test: Deeply nested directory structure (10+ levels)
- [ ] Test: Very long post (10MB markdown file)
- [ ] Test: 100+ posts in single category (pagination)

## Implementation Notes

### Test Fixtures Structure
```
tests/
├── fixtures/
│   ├── minimal_site/
│   │   ├── content/
│   │   │   └── hello.md
│   │   ├── templates/
│   │   │   └── default.html
│   │   └── config.toml
│   ├── multi_category/
│   │   ├── content/
│   │   │   ├── python/
│   │   │   │   ├── intro.md
│   │   │   │   └── advanced.md
│   │   │   └── rust/
│   │   │       └── ownership.md
│   │   └── templates/
│   │       ├── default.html
│   │       └── python.html
│   └── pagination_site/
│       ├── content/
│       │   └── posts/ (15 markdown files)
│       └── templates/
│           ├── default.html
│           └── index.html
└── unit/
    ├── test_models.py
    ├── test_metadata.py
    ├── test_templates.py
    ├── test_urls.py
    ├── test_cache.py
    ├── test_indexes.py
    └── test_stages.py
```
