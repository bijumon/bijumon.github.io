---
title: pgen - a python static site generator
---
Here’s my attempt at creating a useful Python script: a static site generator that converts a folder of Markdown files into HTML. This project uses Python 3.12, `uv` for managing external dependencies, and supports either TOML or YAML front matter. We'll rely on `mistletoe` for Markdown conversion and `jinja2` for HTML templating.

The script makes use of the following:

- list for file handling
- pathlib for directory management
- dict for data storage
- f-strings for generating permalinks
