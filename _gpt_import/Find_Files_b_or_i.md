## user
in shell, find files starting with b or i
## assistant

To find files starting with `b` or `i` in the shell, you can use the `ls` command with a wildcard pattern and the `-d` option to list only directories. Here is the command you would use:

```sh
ls -d [bi]*
```

This command breaks down as follows:
- `ls`: The list command.
- `-d`: Option to list directories.
- `[bi]`: A character class that matches either `b` or `i`.
- `*`: A wildcard that matches any number of characters.

This will list all files and directories in the current directory that start with either `b` or `i`. If you want to search recursively within subdirectories, you can use the `find` command:

```sh
find . -type f \( -name "b*" -o -name "i*" \)
```

This command breaks down as follows:
- `find .`: Start searching in the current directory.
- `-type f`: Only look for files (if you want directories too, you can omit this part).
- `\( -name "b*" -o -name "i*" \)`: Look for files with names starting with `b` or `i`.
## user
how can i set a starship shell preset
## assistant
To set a Starship shell preset, you'll need to create or modify the configuration file for Starship. Here are the steps to do this:

1. **Install Starship**: If you haven't already installed Starship, you can install it using the following command for your specific package manager. For example, using `curl` and `sh`:

    ```sh
    curl -sS https://starship.rs/install.sh | sh
    ```

2. **Configure Starship**:
    - Create or open the Starship configuration file located at `~/.config/starship.toml`.

3. **Set a Preset**:
    - You can copy a preset configuration into the `starship.toml` file. Below is an example of a simple preset configuration:

    ```toml
    # ~/.config/starship.toml

    [prompt]
    add_newline = false
    prompt_order = [
      "username",
      "hostname",
      "directory",
      "git_branch",
      "git_status",
      "cmd_duration",
      "line_break",
      "jobs",
      "battery",
      "time",
      "character"
    ]

    [directory]
    truncation_length = 3

    [git_branch]
    symbol = "🌿 "

    [git_status]
    show_sync_count = true

    [character]
    success_symbol = "[➜](bold green)"
    error_symbol = "[➜](bold red)"
    ```

4. **Reload Your Shell**:
    - To apply the changes, you need to reload your shell or source your configuration file. For example, if you are using `bash` or `zsh`, you can run:

    ```sh
    source ~/.bashrc    # for bash
    source ~/.zshrc     # for zsh
    ```

5. **Verify Configuration**:
    - Open a new terminal window or tab to see the changes take effect. The prompt should now reflect the Starship configuration you specified.

By following these steps, you can set and customize a Starship shell preset to enhance your terminal prompt.