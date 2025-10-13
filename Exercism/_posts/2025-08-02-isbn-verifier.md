---
date: 2025-08-02 16:34:54 +0530
---

``` python
"""
check an ISBN-10 number is valid by computing a checksum, as per the ISBN-10 validation formula.
"""

def is_valid(isbn: str) -> bool:
    digits = [10 if c == 'X' and i == 9 else int(c) if c.isdigit() else None 
              for i, c in enumerate(c for c in isbn if c.isalnum())]

    if len(digits) != 10 or any(d is None for d in digits):
        return False

    result = sum(d * (10 - i) for i, d in enumerate(digits))
    return result % 11 == 0

```
