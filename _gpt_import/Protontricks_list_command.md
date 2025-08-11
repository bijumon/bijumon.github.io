## user
protontricks list installed for game
## assistant

To list installed packages for a specific game using `protontricks`, follow these steps:

1. First, find the game's Steam App ID. You can look it up on [SteamDB](https://steamdb.info/) or check your Steam game library. 

2. Once you have the App ID, run the following command to list installed packages for that specific game:

   ```bash
   protontricks <AppID> list
   ```

Replace `<AppID>` with the actual App ID of your game.

For example, if the App ID is `123456`, the command would look like:

   ```bash
   protontricks 123456 list
   ```

This will show you a list of all installed packages (like DirectX, .NET, etc.) for that game.