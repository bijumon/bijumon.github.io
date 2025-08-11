## user
how to remove data and completely uninstall waydroid
## assistant

To completely uninstall Waydroid and remove all associated data, follow these steps. This guide assumes you're on a Linux-based system, as Waydroid is commonly used on Linux.

### 1. Stop Waydroid Services
Before uninstalling, ensure Waydroid is not running:

```bash
sudo waydroid session stop
```

### 2. Uninstall Waydroid
Depending on how you installed it, use one of the following commands:

- **For systems with APT (Debian, Ubuntu):**

    ```bash
    sudo apt purge waydroid -y
    ```

- **For systems with `yay` (Arch-based):**

    ```bash
    yay -Rns waydroid
    ```

### 3. Remove Waydroid Data
Waydroid stores data in the following directories. Use these commands to delete them:

```bash
sudo rm -rf /var/lib/waydroid
sudo rm -rf /usr/lib/waydroid
sudo rm -rf /etc/waydroid
```

Additionally, Waydroid creates network settings, so it’s a good idea to remove any related network configurations:

```bash
sudo rm -rf /usr/lib/systemd/system/waydroid-*.service
```

### 4. Optional: Remove Kernel Modules (if installed)
If you installed Waydroid kernel modules (like `binder_linux`), you might want to remove them. However, this step is only necessary if you manually installed these modules.

1. **List Modules**: 

    ```bash
    lsmod | grep binder_linux
    ```

2. **Remove Modules (if loaded)**: 

    ```bash
    sudo modprobe -r binder_linux
    ```

3. **Blacklist Modules (to prevent autoloading)**: 

    Edit the blacklist file:

    ```bash
    sudo nano /etc/modprobe.d/waydroid-blacklist.conf
    ```

    Add:

    ```plaintext
    blacklist binder_linux
    blacklist ashmem_linux
    ```

4. Update the kernel modules:

    ```bash
    sudo update-initramfs -u
    ```

### 5. Reboot
Finally, restart your computer to ensure all Waydroid services and modules are unloaded.

This will completely remove Waydroid and its associated data from your system.