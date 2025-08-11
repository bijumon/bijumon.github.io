## user
rsync command for copying a folder while skipping over existing changes if thier cheksum matcher
## assistant

To copy a folder with `rsync` and **skip files that haven't changed based on checksum**, you can use the `--checksum` (`-c`) option.

Here’s the command:

```bash
rsync -avc /source/folder/ /destination/folder/
```

### Explanation:
- `-a` = archive mode (preserves permissions, symbolic links, etc.)
- `-v` = verbose
- `-c` = use checksum to compare files instead of just size and modified time

### Important Notes:
- The trailing slashes matter: `/source/folder/` means "contents of folder", not the folder itself.
- Using `--checksum` can be **slower**, because it calculates checksums for every file on both sides before deciding what to copy.

If you don’t want to re-copy files that are already identical (by checksum), this is the right option.

Let me know if you want it to delete files that don’t exist on the source side (`--delete`), or if you're syncing over SSH.
## user
rsync command for copying a folder while skipping over existing changes if thier checksum matches
## assistant

To copy a folder using `rsync` while **skipping files whose content hasn't changed** (i.e., their checksums match), you can use the `--checksum` (`-c`) option. This makes `rsync` compare files based on checksums instead of just file size and modification time.

Here's the command:

```bash
rsync -avc /source/folder/ /destination/folder/
```

### Breakdown:
- `-a`: Archive mode (preserves symbolic links, permissions, timestamps, etc.)
- `-v`: Verbose (optional, shows progress)
- `-c`: Use checksum to determine if files have changed

### Notes:
- **`--checksum` is slower** than relying on modification time and size, because it requires reading every file entirely to calculate the checksum.
- The trailing slashes in `/source/folder/` ensure that the *contents* of the folder are copied, not the folder itself.

Let me know if you want to exclude specific files or see a dry run version before actually copying.