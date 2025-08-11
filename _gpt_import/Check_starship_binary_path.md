## user
Write a shell script to check if starship binary exists in path and execute 'starship init bash' if it does
## assistant

Here's a shell script that checks whether the `starship` binary exists in the system's `PATH`, and if so, runs `starship init bash`:

```bash
#!/bin/bash

# Check if 'starship' is available in PATH
if command -v starship >/dev/null 2>&1; then
    # Run starship init for bash
    eval "$(starship init bash)"
else
    echo "starship not found in PATH."
fi
```

### Usage:
1. Save this as `init_starship.sh`.
2. Make it executable:
   ```bash
   chmod +x init_starship.sh
   ```
3. You can run it directly, or **source it** if you want the prompt changes to affect your current shell:
   ```bash
   source ./init_starship.sh
   ```

> ✅ **Note:** For use in `.bashrc` or `.bash_profile`, use the script body directly instead of calling the script file to avoid unnecessary subshells.