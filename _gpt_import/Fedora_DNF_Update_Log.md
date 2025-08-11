## user
fedora dnf show recent updates log
## assistant

To view the recent updates log in Fedora using `dnf`, you can use the following methods:

### 1. Check Recent Updates
Run this command to see recent updates applied to your system:

```bash
dnf history
```

This will list a history of transactions (installations, updates, and removals), including their transaction ID, command, date, and summary. 

### 2. View Details of a Specific Transaction
To see detailed information about a specific transaction, use:

```bash
dnf history info <transaction-id>
```

Replace `<transaction-id>` with the ID of the transaction you want to inspect (from the `dnf history` output).

### 3. Check the Log File
DNF maintains a log file at `/var/log/dnf.log`. You can use `tail` to quickly check the most recent activity:

```bash
tail -n 50 /var/log/dnf.log
```

Or open it with a text editor:

```bash
nano /var/log/dnf.log
```

### 4. Use `journalctl` for Package Updates
You can also use `journalctl` to review logs related to package management:

```bash
journalctl -u dnf-automatic.service
```

If you're not using `dnf-automatic`, filter all system updates with:

```bash
journalctl | grep "dnf"
```

These methods will help you inspect recent updates and other package management activities on Fedora. Let me know if you need further clarification!