## user
systemd rotate and clean logs
## assistant

In **systemd**, log files are handled by the `journald` service. System logs are stored in the binary journal format, typically in `/var/log/journal/`. If this directory doesn't exist, logs are stored in memory and cleared on reboot.

Here’s how you can **rotate and clean logs** effectively:

---

### 1. **Control Log Size with Journald Configuration**
`journald` automatically rotates logs based on size or time. You can configure it in `/etc/systemd/journald.conf`.

#### Steps:
1. Open the configuration file:
   ```bash
   sudo nano /etc/systemd/journald.conf
   ```

2. Modify or add the following options:
   - `SystemMaxUse=`: Maximum disk space used by logs.
   - `SystemKeepFree=`: Minimum free space to leave on disk.
   - `SystemMaxFileSize=`: Maximum size of an individual journal file.
   - `SystemMaxFiles=`: Maximum number of files to retain.

   Example:
   ```ini
   [Journal]
   SystemMaxUse=500M
   SystemKeepFree=50M
   SystemMaxFileSize=100M
   SystemMaxFiles=10
   ```

3. Restart `journald` to apply changes:
   ```bash
   sudo systemctl restart systemd-journald
   ```

---

### 2. **Manually Rotate Logs**
Systemd rotates logs automatically when they reach the configured size. However, you can force rotation with:
```bash
sudo journalctl --rotate
```

---

### 3. **Clean Old Logs**
To clean logs older than a specific time or to free up space, use `journalctl`:

#### Examples:
- Remove logs older than 2 weeks:
  ```bash
  sudo journalctl --vacuum-time=2weeks
  ```
- Reduce logs to occupy no more than 100 MB:
  ```bash
  sudo journalctl --vacuum-size=100M
  ```
- Keep only the last 5 log files:
  ```bash
  sudo journalctl --vacuum-files=5
  ```

---

### 4. **Check Current Log Usage**
To see how much space logs are using:
```bash
journalctl --disk-usage
```

---

### 5. **Delete All Logs**
To completely wipe all logs:
```bash
sudo rm -rf /var/log/journal/*
sudo systemctl restart systemd-journald
```

---

These methods ensure efficient log management while keeping disk space under control. Let me know if you need assistance with any specific step!
## user
delete archived logs
## assistant
To delete **archived logs** in `systemd-journald`, follow these steps:

---

### 1. **Understand Archived Logs**
Archived logs are older journal files that are not actively written to. They are stored in `/var/log/journal/`, if persistent logging is enabled.

To check the logs:
```bash
ls /var/log/journal/$(hostname)/
```
Files with `.journal~` are archived logs.

---

### 2. **Delete Archived Logs with `journalctl`**
Use `journalctl` to remove archived logs:

- Delete logs older than a specific duration:
  ```bash
  sudo journalctl --vacuum-time=2weeks
  ```
  Replace `2weeks` with the desired time frame (e.g., `1month`, `10days`, etc.).

- Delete logs based on size:
  ```bash
  sudo journalctl --vacuum-size=100M
  ```
  This retains only 100 MB of the most recent logs.

- Delete logs to keep only a specific number of files:
  ```bash
  sudo journalctl --vacuum-files=5
  ```

---

### 3. **Manually Delete Archived Logs**
If you want to delete archived logs manually:

1. Locate the journal files:
   ```bash
   sudo ls /var/log/journal/$(hostname)/
   ```

2. Delete the files ending with `.journal~`:
   ```bash
   sudo rm /var/log/journal/$(hostname)/*.journal~
   ```

3. Restart the journald service:
   ```bash
   sudo systemctl restart systemd-journald
   ```

---

### 4. **Check Disk Usage After Cleanup**
Verify the cleanup by checking disk usage:
```bash
journalctl --disk-usage
```

---

These steps ensure only the desired logs are retained and older or archived logs are removed effectively. Let me know if you need further clarification!