## user
zip a directory cmdline
## assistant

To zip a directory from the command line, you can use the `zip` command. Here's how:

### Syntax
```bash
zip -r output.zip directory_name
```

### Explanation:
- `zip`: The command to create a zip archive.
- `-r`: Recursively include files and directories.
- `output.zip`: The name of the zip file you want to create.
- `directory_name`: The name of the directory you want to compress.

### Example
To zip a directory named `my_folder` into a file called `my_folder.zip`:
```bash
zip -r my_folder.zip my_folder
```

### Additional Options:
- Exclude files:
  ```bash
  zip -r output.zip directory_name -x "*.log"
  ```
  This excludes all `.log` files.
  
- Add password protection:
  ```bash
  zip -r -e output.zip directory_name
  ```
  You'll be prompted to enter a password.

If you don't have the `zip` utility installed, you can install it using your package manager:
- On **Debian/Ubuntu**:
  ```bash
  sudo apt install zip
  ```
- On **Fedora/CentOS**:
  ```bash
  sudo dnf install zip
  ```