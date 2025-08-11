## user
zip a folder in linux
## assistant

To zip a folder in Linux, you can use the `zip` command. Here's a step-by-step guide:

1. **Open the terminal**.
2. **Navigate to the directory** where the folder you want to zip is located. For example:
   ```bash
   cd /path/to/directory
   ```
3. **Use the `zip` command** to create a zip archive. The syntax is:
   ```bash
   zip -r output.zip folder_name
   ```
   - `-r` means to recursively zip the contents of the folder.
   - `output.zip` is the name you want for the resulting zip file.
   - `folder_name` is the name of the folder you want to zip.

For example, to zip a folder named `my_folder` into a file named `my_folder.zip`, you would use:
```bash
zip -r my_folder.zip my_folder
```

### Example

```bash
cd /home/user/documents
zip -r my_folder.zip my_folder
```

This command will create a file named `my_folder.zip` in the `/home/user/documents` directory containing all the files and subdirectories within `my_folder`.