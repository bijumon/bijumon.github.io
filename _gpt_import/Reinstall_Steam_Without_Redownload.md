## user
Reinstall steam linux without reinstalling all the games
## assistant

You can reinstall Steam on Linux without having to reinstall all your games by following these steps:

1. **Backup Your Steam Games:**
   - The games are typically stored in the `~/.steam/steam/steamapps/common/` directory. 
   - Copy the entire `common` folder to a safe location outside the Steam directory (e.g., another folder in your home directory or an external drive).

2. **Uninstall Steam:**
   - Depending on your Linux distribution, you can uninstall Steam using your package manager. For example:
     - On Ubuntu/Debian: `sudo apt remove steam`
     - On Fedora: `sudo dnf remove steam`
     - On Arch Linux: `sudo pacman -R steam`

3. **Reinstall Steam:**
   - Install Steam again using your package manager:
     - On Ubuntu/Debian: `sudo apt install steam`
     - On Fedora: `sudo dnf install steam`
     - On Arch Linux: `sudo pacman -S steam`

4. **Restore Your Games:**
   - After reinstalling Steam, move your backup `common` folder back to the `~/.steam/steam/steamapps/` directory.

5. **Re-scan Library Folders:**
   - Open Steam, go to **Steam** > **Settings** > **Downloads** > **Steam Library Folders**.
   - Add the folder where your games are located if it's not already there.
   - Steam should detect the existing games and make them available without requiring a new download.

6. **Verify Game Files (Optional):**
   - If any issues arise, you can verify the integrity of game files by right-clicking on each game in your library, selecting **Properties**, then **Installed Files**, and clicking on **Verify integrity of game files**.

This method ensures that your game data is preserved, avoiding the need to redownload all your games.