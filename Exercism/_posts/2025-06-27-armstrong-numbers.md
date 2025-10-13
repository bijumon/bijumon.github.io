---
date: Fri Jun 27 18:27:39 2025 +0530
---

``` python
"""
Determine whether a number is an Armstrong number
"""

def is_armstrong_number(number):
    digits = [int(d) for d in str(number)]

    length = len(digits)
    total = 0
    for num in digits:
        total += (num ** length)
    return number == total

```
