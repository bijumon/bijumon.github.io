## user
blender debug render commandline
## assistant

In Blender, the command-line render feature is useful for debugging or rendering projects without launching the full graphical interface. The basic syntax is:

```bash
blender -b <blend-file> -f <frame-number>
```

Here’s what the flags mean:
- `-b` runs Blender in background mode (no GUI).
- `<blend-file>` is the path to the `.blend` file.
- `-f` specifies the frame to render.

### Debugging Render Example
If you want to enable detailed logging for debugging purposes during rendering, use the `--debug` flag:

```bash
blender -b <blend-file> -f <frame-number> --debug
```

This will output detailed logs about Blender's operations during the rendering process.

### Example Commands
1. Render a specific frame in debug mode:
   ```bash
   blender -b project.blend -f 10 --debug
   ```

2. Render an animation (frame range):
   ```bash
   blender -b project.blend -s 1 -e 100 -a --debug
   ```
   - `-s`: Start frame.
   - `-e`: End frame.
   - `-a`: Render animation.

3. Save render output to a specific directory:
   ```bash
   blender -b project.blend -o //output/ -f 10 --debug
   ```
   - `-o <path>` specifies the output path. Use `//` for relative paths.

4. Log debug information to a file:
   ```bash
   blender -b project.blend -f 10 --debug > debug_log.txt 2>&1
   ```
   This redirects Blender's output (stdout and stderr) to `debug_log.txt`.

### Useful Additional Flags
- `--debug-all`: Enables all debugging categories.
- `--debug-memory`: Tracks memory usage.
- `--debug-python`: Debugs Python scripts.
- `--threads <n>`: Sets the number of CPU threads to use.
- `--factory-startup`: Ignores user preferences to use factory settings for debugging.

These commands provide detailed logs that can help diagnose issues with rendering, scripts, or configurations.