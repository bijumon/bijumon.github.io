---
date: Sun May 04 17:26:53 2025 +0530
---

``` python
"""
from a matrix of numbers, return the rows and columns of that matrix
"""

class Matrix:
    def __init__(self, matrix_string):
        rowStrings = [r.split() for r in matrix_string.splitlines()]
        self.matrix = [[int(num) for num in row] for row in rowStrings]

    def row(self, index):
        return self.matrix[index - 1]

    def column(self, index):
        return [ column[index - 1] for column in self.matrix]
```
