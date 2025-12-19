---
date: 2025-08-03 15:59:04 +0530
---

``` python
"""
Calculate the points scored in a single toss of a Darts game.
"""

import math 

def score(x: float, y: float) -> int:
    distance = math.sqrt(x**2 + y**2)
    if distance <= 1:
        return 10
    elif distance <= 5:
        return 5
    elif distance <= 10:
        return 1
    else:
        return 0
```
