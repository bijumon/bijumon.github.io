## user
uv pip install to ~/.local
## assistant

To install a Python package using `uv` into your `~/.local` directory (i.e., user site-packages), you can use the `--target` option:

```bash
uv pip install <package-name> --target ~/.local/lib/python3.X/site-packages
```

Replace `python3.X` with your actual Python version, like `python3.11`.

### Alternatively:
If you want behavior similar to `pip install --user`, `uv` doesn't yet support `--user` directly as of early 2025. But you can use a workaround by explicitly setting the environment variable:

```bash
PYTHONUSERBASE=~/.local uv pip install <package-name> --target ~/.local/lib/python3.X/site-packages
```

Then, make sure `~/.local/bin` is in your `PATH`, and Python can find your local site-packages.

### To check your Python version:
```bash
python3 --version
```

Let me know if you want a one-liner script or alias for convenience.