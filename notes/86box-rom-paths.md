---
layout: "post"
title: "86Box ROM Paths"
date: "2026-02-08"
---

# 86Box default rom path on linux #

On Linux, **86Box** looks for ROMs in a pretty straightforward, XDG-friendly place.

### Default ROM directory
**System-wide install**
```text
/usr/share/86box/roms/
```

That’s where distro packages usually drop the ROM set.

### Per-user ROM directory
```text
~/.local/share/86box/roms/
```

Anything you put here will override or supplement the system ROMs.

### Config file (handy for checking)
Your config lives at:
```text
~/.config/86box/86box.cfg
```

If you ever changed the ROM path, you’ll see something like:
```ini
rom_path = /some/custom/path
```

### Quick sanity check
From a terminal:
```bash
ls /usr/share/86box/roms
ls ~/.local/share/86box/roms
```

If neither exists, 86Box will complain at startup about missing ROMs.

