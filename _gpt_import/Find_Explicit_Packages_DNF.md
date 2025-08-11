## user
how to find explicitly installed packages using dnf
## assistant

To list explicitly installed packages with `dnf`, use the following command:

```bash
dnf repoquery --userinstalled
```

This command will display only the packages that were installed manually by the user, excluding those installed as dependencies. 

Alternatively, you can also use:

```bash
dnf history userinstalled
```

This lists packages in the format showing what was specifically marked by the user as "installed," useful for identifying user-added software in a longer list of installed items.