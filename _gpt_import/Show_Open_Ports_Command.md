## user
use firewall-cmd to show all open ports
## assistant

You can use the `firewall-cmd` command to list all open ports on your system. Here's how to do it:

1. **Show all open ports in the current zone:**

   ```bash
   sudo firewall-cmd --list-ports
   ```

   This command lists all open ports in the default (or currently active) zone.

2. **Show all open ports in a specific zone:**

   If you want to check open ports for a specific zone (e.g., `public` or `home`), use:

   ```bash
   sudo firewall-cmd --zone=ZONE_NAME --list-ports
   ```

   Replace `ZONE_NAME` with the name of the zone you want to inspect.

3. **Show all open ports across all zones:**

   To see open ports for all zones, use:

   ```bash
   sudo firewall-cmd --list-all --zone=ZONE_NAME
   ```

   This command will display detailed information for the specified zone, including open ports.

4. **Show all configurations (including ports) across all zones:**

   ```bash
   sudo firewall-cmd --list-all-zones
   ```

   This will display the open ports for each zone along with other settings.

These commands are helpful for auditing your firewall configuration and ensuring that only the necessary ports are open.