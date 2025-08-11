## user
using sed add the line '%global optflags -O2 -g -pipe -Wall -Werror=format-security -march=znver4' to file.spec
## assistant

To add the line `%global optflags -O2 -g -pipe -Wall -Werror=format-security -march=znver4` to `file.spec` using `sed`, you can insert it at a specific position in the file. For example:

### Add at the beginning:
```bash
sed -i '1i %global optflags -O2 -g -pipe -Wall -Werror=format-security -march=znver4' file.spec
```

### Add at the end:
```bash
sed -i '$a %global optflags -O2 -g -pipe -Wall -Werror=format-security -march=znver4' file.spec
```

### Add after a specific line (e.g., after `%build`):
If you want to insert it after a line containing `%build`:
```bash
sed -i '/%build/a %global optflags -O2 -g -pipe -Wall -Werror=format-security -march=znver4' file.spec
```

Replace `%build` with the relevant line or pattern if needed.