---
date: 2025-08-02 08:55:41 +0530
---

``` python
"""
A pangram is a sentence using every letter of the alphabet at least once.
It is case insensitive, so it doesn't matter if a letter is lower-case (e.g. `k`) or upper-case (e.g. `K`).

Is a sentence a pangram ?
"""

def is_pangram(sentence: str) -> bool:
    alphabets = list("abcdefghijklmnopqrstuvwxyz")

    for char in alphabets:
        if char not in sentence.lower():
            return False
    return True
```
