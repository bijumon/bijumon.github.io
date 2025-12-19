---
date: 2025-07-30 11:51:33 +0530
---

``` python
"""
Given a string containing brackets `[]`, braces `{}`, parentheses `()`, or any combination thereof, verify that any and all pairs are matched and nested correctly
"""

def is_paired(text: str) -> bool:
    pairs = { '}':'{', ']':'[', ')':'(' }
    brackets = []
    for chr in text:
        if chr in '{[(':
            brackets.append(chr)
        elif chr in '}])':
            if not brackets or brackets.pop() != pairs[chr]:
                return False
    return not brackets
```
