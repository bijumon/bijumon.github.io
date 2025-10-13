---
date: 2025-07-31 17:24:06 +0530
---

``` python
"""
Implement of the rotational cipher, also sometimes called the Caesar cipher.
"""

def rotate(text: str, key: int) -> str:
    chars = "abcdefghijklmnopqrstuvwxyz"

    new_chars = chars[key:] + chars[:key]
    trans_table = str.maketrans(chars + chars.upper(), new_chars + new_chars.upper())
    return text.translate(trans_table)

```
