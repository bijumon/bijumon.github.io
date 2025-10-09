# Jekyll Commonmarker Plugin

A Jekyll plugin that provides full access to all Commonmarker options and extensions, allowing you to customize markdown processing beyond what `jekyll-commonmark` provides.

## Features

- ✅ Full access to all Commonmarker parse, render, and extension options
- ✅ Configurable syntax highlighting with multiple themes
- ✅ Support for GitHub Flavored Markdown extensions
- ✅ No hardcoded options - everything is configurable via `_config.yml`
- ✅ Support for advanced extensions (footnotes, description lists, math, wikilinks, etc.)

## Installation

### 1. Add the gem to your Gemfile

```ruby
gem 'commonmarker'
```

Then run:
```bash
bundle install
```

### 2. Add the plugin file

Save the plugin code as `_plugins/commonmarker.rb` in your Jekyll site directory.

### 3. Configure in _config.yml

Set the markdown processor and configure options:

```yaml
markdown: Commonmarker

commonmarker:
  parse:
    smart: true
  extension:
    table: true
    strikethrough: true
    autolink: true
```

## Configuration

All options are optional. If you don't specify a section, sensible defaults will be used.

### Parse Options

Control how markdown is parsed:

```yaml
commonmarker:
  parse:
    smart: true                        # Smart punctuation
    default_info_string: ""            # Default code block language
    relaxed_tasklist_matching: false   # Flexible task list syntax
    relaxed_autolinks: false           # Relaxed URL recognition
```

### Render Options

Control HTML output:

```yaml
commonmarker:
  render:
    hardbreaks: true                   # Convert \n to <br>
    github_pre_lang: true              # Use GitHub-style code blocks
    unsafe: false                      # Allow raw HTML (be careful!)
    sourcepos: false                   # Add source position attributes
    width: 80                          # Target line width
```

### Extension Options

Enable markdown extensions:

```yaml
commonmarker:
  extension:
    # GitHub Flavored Markdown
    strikethrough: true                # ~~strikethrough~~
    table: true                        # Tables
    autolink: true                     # Auto-link URLs
    tasklist: true                     # - [x] Task items
    tagfilter: true                    # Filter unsafe HTML tags
    
    # Additional Extensions
    footnotes: true                    # Footnotes[^1]
    superscript: true                  # ^superscript^
    subscript: true                    # ~subscript~
    description_lists: true            # Definition lists
    math_dollars: true                 # $math$ and $$math$$
    shortcodes: true                   # :emoji: codes
    underline: true                    # ++underline++
    spoiler: true                      # ||spoiler||
    alerts: true                       # GitHub-style alerts
    
    # Header IDs
    header_ids: "user-content-"        # Prefix for auto-generated IDs
    
    # Front matter
    front_matter_delimiter: "---"      # YAML front matter support
    
    # Wikilinks
    wikilinks_title_after_pipe: true   # [[link|Title]] format
```

### Plugin Options

Configure additional processing plugins:

```yaml
commonmarker:
  plugins:
    syntax_highlighter:
      theme: "InspiredGitHub"          # Use a built-in theme
```

**Available syntax highlighting themes:**
- `base16-ocean.dark` (default)
- `base16-eighties.dark`
- `base16-mocha.dark`
- `base16-ocean.light`
- `InspiredGitHub`
- `Solarized (dark)`
- `Solarized (light)`

**Use CSS classes instead:**
```yaml
commonmarker:
  plugins:
    syntax_highlighter:
      theme: ""                        # Outputs CSS classes
```

**Disable syntax highlighting:**
```yaml
commonmarker:
  plugins:
    syntax_highlighter: false
```

**Use custom theme directory:**
```yaml
commonmarker:
  plugins:
    syntax_highlighter:
      theme: "MyCustomTheme"
      path: "./my_themes"              # Directory with .tmtheme files
```

## Common Configuration Examples

### GitHub Flavored Markdown (Default)

```yaml
markdown: Commonmarker
commonmarker:
  extension:
    strikethrough: true
    table: true
    autolink: true
    tasklist: true
    tagfilter: true
```

### Academic/Technical Writing

```yaml
markdown: Commonmarker
commonmarker:
  parse:
    smart: true
  extension:
    footnotes: true
    superscript: true
    subscript: true
    math_dollars: true
    table: true
```

### Maximum Features

```yaml
markdown: Commonmarker
commonmarker:
  parse:
    smart: true
  render:
    hardbreaks: true
  extension:
    strikethrough: true
    table: true
    autolink: true
    tasklist: true
    footnotes: true
    superscript: true
    subscript: true
    description_lists: true
    underline: true
    spoiler: true
    shortcodes: true
    alerts: true
```

## Comparison with jekyll-commonmark

| Feature | jekyll-commonmark | This Plugin |
|---------|------------------|-------------|
| Basic CommonMark | ✅ | ✅ |
| GFM Extensions | Limited | ✅ All |
| Custom Options | Limited | ✅ Full |
| Footnotes | ❌ | ✅ |
| Math Support | ❌ | ✅ |
| Wikilinks | ❌ | ✅ |
| Syntax Themes | ❌ | ✅ |
| Configuration | Hardcoded | Flexible |

## Troubleshooting

### Plugin not loading

Make sure the file is in `_plugins/commonmarker.rb` and your `_config.yml` has:
```yaml
markdown: Commonmarker
```

### Options not working

Check your YAML syntax. Options must be properly indented and use valid YAML:
```yaml
# ✅ Correct
commonmarker:
  parse:
    smart: true

# ❌ Incorrect (wrong indentation)
commonmarker:
parse:
  smart: true
```

### Raw HTML being stripped

Set `unsafe: true` in render options (use with caution):
```yaml
commonmarker:
  render:
    unsafe: true
```

## Documentation

For detailed information about each option:
- [Commonmarker Documentation](https://www.rubydoc.info/gems/commonmarker)
- [Comrak Options](https://github.com/kivikakk/comrak#usage)
- [CommonMark Spec](https://commonmark.org/)
- [GitHub Flavored Markdown Spec](https://github.github.com/gfm/)

## License

This plugin is released into the public domain. Use it however you'd like!
