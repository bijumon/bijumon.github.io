## user
cmake install destination
## assistant

In CMake, the "install destination" is the directory path where built targets (binaries, libraries, headers, etc.) are placed when you run `make install` (or `cmake --install`).

You control it using the `DESTINATION` keyword inside an `install()` command.  
For example:

```cmake
install(TARGETS myapp
    RUNTIME DESTINATION bin   # for executables
    LIBRARY DESTINATION lib   # for shared libraries (.so, .dylib)
    ARCHIVE DESTINATION lib   # for static libraries (.a)
)
```

Or for headers:

```cmake
install(FILES myheader.h
    DESTINATION include
)
```

You can also set a *prefix* globally when you generate your build files:

```bash
cmake -DCMAKE_INSTALL_PREFIX=/your/custom/path ..
```
Then the `DESTINATION` is relative to that prefix.  
So if you install with `DESTINATION bin`, and your prefix is `/opt/myproject`, your executable goes to `/opt/myproject/bin/`.

---

Would you like me to show a full real-world example too? 🚀  
Or are you asking about something more specific like installing to system directories?
## user
cmake install to a dir command


## assistant

In CMake, if you want to **install** built files into a specific **directory**, you control it mainly via the `DESTINATION` in the `install()` command **and** when you run `cmake --install`, you can specify the final directory with `--prefix`.

Here’s a **basic example** of how it works:

In your `CMakeLists.txt`:

```cmake
# Install a target (like an executable or library)
install(TARGETS my_program
    DESTINATION bin
)

# Install a header file
install(FILES my_header.h
    DESTINATION include
)
```

Then, after building:

```bash
cmake --install . --prefix /your/custom/install/path
```

- `--prefix` lets you override the install path at install time.
- So in this case:
  - The binary will end up in `/your/custom/install/path/bin`
  - The header will end up in `/your/custom/install/path/include`

---

**Alternative (in CMake itself):**

You can also control the install prefix at configuration time:

```bash
cmake -DCMAKE_INSTALL_PREFIX=/your/custom/install/path ..
```

and then just:

```bash
cmake --install .
```

---

**Quick summary:**
- In `CMakeLists.txt`: `DESTINATION` controls subfolders.
- At install time:
  - Use `cmake --install . --prefix /path`
- Or at configuration time:
  - Use `-DCMAKE_INSTALL_PREFIX=/path`

---

Would you like me to show a real tiny full project example too? 🚀 (like a `main.cpp` + `CMakeLists.txt` + install to dir)