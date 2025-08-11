## user
use 'fd' fast search to find largest directories
## assistant

`fd` is a blazing-fast alternative to `find`, but by itself, it doesn't provide directory sizes like `du` (disk usage). However, you can combine `fd` with other tools like `du` or `sort` to find the largest directories. Here’s how you can do it:

### 🔍 Find largest directories using `fd` + `du`:

```bash
fd --type d --max-depth 1 . | xargs du -sh 2>/dev/null | sort -hr | head -n 10
```

### Explanation:
- `fd --type d --max-depth 1 .`: finds all directories (not recursively deeper than 1 level).
- `xargs du -sh`: calculates the human-readable sizes of those directories.
- `sort -hr`: sorts the results by size (largest first).
- `head -n 10`: shows the top 10 largest directories.
- `2>/dev/null`: silences permission errors.

### 🔁 For deeper searches:
Increase the depth:

```bash
fd --type d --max-depth 3 . | xargs du -sh 2>/dev/null | sort -hr | head -n 20
```

### 🔧 Alternative without `fd` (pure `du` version):
```bash
du -h --max-depth=1 | sort -hr | head -n 10
```

Let me know if you want to filter for specific directory names or exclude some folders (e.g., `.git`).
## user
pretty print json
## assistant

To **pretty print JSON** from the command line, you can use several tools depending on what's available on your system. Here are common and effective methods:

---

### 🐍 Using Python (built-in on most systems):
```bash
cat file.json | python3 -m json.tool
```

Or from a string:
```bash
echo '{"foo": "bar", "baz": [1, 2, 3]}' | python3 -m json.tool
```

---

### 💡 Using `jq` (recommended if installed):
```bash
jq . file.json
```

From a string:
```bash
echo '{"foo": "bar", "baz": [1,2,3]}' | jq .
```

---

### 🧪 Using `yq` (also handles YAML):
```bash
yq -P . file.json
```

---

### 🧷 Want to write pretty JSON to a file?
```bash
jq . input.json > pretty.json
```

---

Let me know if you want compact JSON instead (minified) or colored output.