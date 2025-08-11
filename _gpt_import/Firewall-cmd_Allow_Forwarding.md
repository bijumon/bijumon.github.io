## user
what is the firewall-cmd equivalent for ' ufw default allow FORWARD'
## assistant

To set the default `FORWARD` policy to `ALLOW` using `firewall-cmd`, you can achieve this by modifying the zone configuration. However, note that `firewalld` does not directly expose forwarding rules like `iptables` or `ufw` does. Instead, it uses zones and services.

Here’s how to allow forwarding:

### Step 1: Enable IPv4 and/or IPv6 forwarding
You need to enable packet forwarding at the system level first.

#### For IPv4:
Edit the sysctl configuration:
```bash
sudo sysctl -w net.ipv4.ip_forward=1
```

To make it permanent, add the following line to `/etc/sysctl.conf`:
```bash
net.ipv4.ip_forward = 1
```

#### For IPv6:
```bash
sudo sysctl -w net.ipv6.conf.all.forwarding=1
```

Add to `/etc/sysctl.conf`:
```bash
net.ipv6.conf.all.forwarding = 1
```

Then reload the configuration:
```bash
sudo sysctl -p
```

### Step 2: Allow Forwarding in the Firewalld Configuration

#### Add Masquerading (if applicable):
If you're doing NAT or routing, you might want to enable masquerading:
```bash
sudo firewall-cmd --permanent --zone=public --add-masquerade
```

#### Set Forward Policy for a Zone:
To explicitly allow forwarding in a zone (like `public`):
```bash
sudo firewall-cmd --permanent --zone=public --add-forward-port=port=0:proto=all:toaddr=0.0.0.0
```

This will allow all forwarding through the zone.

### Step 3: Reload Firewalld
Finally, reload the firewall to apply the changes:
```bash
sudo firewall-cmd --reload
```

This method configures `firewalld` to allow forwarding similar to `ufw default allow FORWARD`. However, it's always good to manage zones properly to ensure your system's security policies are not too permissive.
## assistant

In `firewalld`, the equivalent of `ufw default allow FORWARD` is to modify the forwarding policy. While `ufw` uses a simpler syntax, `firewalld` requires a couple of commands to set up forwarding.

To allow all forwarded traffic in `firewalld`, you can use the following command:

```bash
firewall-cmd --set-target=ACCEPT --zone=zone_name
```

Replace `zone_name` with the appropriate zone (like `public`, `internal`, etc.) for which you want to allow forwarding.

Additionally, you need to enable IP forwarding in your system settings:

1. Open the configuration file:
   ```bash
   sudo nano /etc/sysctl.conf
   ```

2. Uncomment or add the following line:
   ```bash
   net.ipv4.ip_forward = 1
   ```

3. Apply the changes:
   ```bash
   sudo sysctl -p
   ```

You can also use the `--permanent` option with `firewall-cmd` to make the change persistent across reboots:

```bash
firewall-cmd --zone=zone_name --add-masquerade --permanent
firewall-cmd --reload
```

Remember to check the active zones and their rules with:

```bash
firewall-cmd --get-active-zones
```

This will help you identify which zone you should modify.