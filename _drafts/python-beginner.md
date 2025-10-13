---
---

[python: how to check if a line is an empty line - Stack Overflow](https://stackoverflow.com/questions/7896495/python-how-to-check-if-a-line-is-an-empty-line)

If you want to ignore lines with only whitespace:

``` python
if line.strip():
    ... do something
```

The empty string is a False value.

Or if you really want only empty lines:

``` python
if line in ['\n', '\r\n']:
    ... do  something
```