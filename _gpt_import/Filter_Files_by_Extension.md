## user
rewrite [f for f in files if f.endswith(".md") or f.endswith('.jinja2')] to check endswith from a list
## assistant
You can achieve that by creating a list of file extensions and then checking if the file ends with any of those extensions. Here's how you can rewrite the given expression:

```python
file_extensions = [".md", ".jinja2"]
filtered_files = [f for f in files if any(f.endswith(ext) for ext in file_extensions)]
```

This code first creates a list `file_extensions` containing the desired file extensions. Then, it iterates over `files`, checking if each file `f` ends with any of the extensions in `file_extensions`. If it does, the file is included in the `filtered_files` list.
## assistant
You can achieve the same filtering by checking if the file ends with any of the extensions listed in a separate list. Here's how you could rewrite it:

```python
extensions = [".md", ".jinja2"]
filtered_files = [f for f in files if any(f.endswith(ext) for ext in extensions)]
``` 

This code iterates over each file in `files`, checking if its extension matches any extension in the `extensions` list. If it does, it adds that file to `filtered_files`.