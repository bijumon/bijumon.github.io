## user
how can i store darktable config in ~/.local/share/darktable instead of ~/Pictures
## assistant

Darktable does **not** store its configuration in `~/Pictures` — that directory is used **by default** to **open/import photos** (i.e. the default image folder), not to store configuration data.

Here's how Darktable's storage typically works:

---

### 🔧 **Configuration and Data Directories**

By default, Darktable stores its data in:

- **Config files** (preferences, UI layout, etc.):  
  `~/.config/darktable/`

- **Library/database/cache data** (thumbnails, XMP sidecars, etc.):  
  `~/.cache/darktable/`  
  `~/.local/share/darktable/`

These follow the [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html).

---

### 📁 Why You See `~/Pictures`

When you launch Darktable, it defaults to showing the contents of `~/Pictures` for convenience. It's just the default **import location** for images, not a config path.

---

### ✅ What You Can Do

If you're asking how to **ensure all user data** (especially the library/database/cache) is stored in `~/.local/share/darktable`, you can use the `--configdir` option when launching Darktable:

```bash
darktable --configdir ~/.local/share/darktable
```

But note:
- This overrides the entire config dir and moves both preferences and library.
- It will **not use `~/.config/darktable` anymore** when this is set.
- Useful for portable or sandboxed setups.

---

### 📝 Tip: Creating a Desktop Entry

If you want to always launch Darktable with this custom config dir, edit or create a `.desktop` file like this:

```ini
[Desktop Entry]
Name=Darktable (Custom Config)
Exec=darktable --configdir ~/.local/share/darktable
Type=Application
Icon=darktable
Categories=Graphics;
```

---

Would you like help copying your existing settings from `~/.config/darktable/` to `~/.local/share/darktable/` before switching?