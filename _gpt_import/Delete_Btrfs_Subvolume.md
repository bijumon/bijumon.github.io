## user
Delete btrfs subvolume @home
## assistant

To delete a Btrfs subvolume, such as `@home`, follow these steps:

1. **Unmount the subvolume** (if mounted):
   ```bash
   sudo umount /path/to/mount/point
   ```

2. **Delete the subvolume**:
   ```bash
   sudo btrfs subvolume delete /path/to/subvolume/@home
   ```

   If the subvolume is mounted at `/home`, you would run:
   ```bash
   sudo btrfs subvolume delete /home
   ```

3. **Optional**: You can check if the subvolume is deleted using:
   ```bash
   sudo btrfs subvolume list /mnt
   ```

Make sure you replace `/path/to/subvolume` with the correct path where your subvolume resides. If you're deleting the root subvolume or system-critical subvolumes, ensure you have backups before proceeding.