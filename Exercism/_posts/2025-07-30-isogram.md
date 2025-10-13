---
date: 2025-07-30 13:02:03 +0530
---

``` python
"""
Determine if a word or phrase is an isogram.

An isogram (also known as a "non-pattern word") is a word or phrase without a repeating letter, however spaces and hyphens are allowed to appear multiple times.

Examples of isograms:

- lumberjacks
- background
- downstream
- six-year-old

The word _isograms_, however, is not an isogram, because the s repeats.
"""

def is_isogram(text: str) -> bool:
    chars = ''.join(filter(str.isalnum, text)).lower()
    return len(chars) == len(set(chars))

```
