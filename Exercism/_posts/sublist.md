---
date: 2025-08-06 12:14:51 +0530
---

``` python
"""
This exercise stub and the test suite contain several enumerated constants.

Enumerated constants can be done with a NAME assigned to an arbitrary,
but unique value. An integer is traditionally used because it’s memory
efficient.
It is a common practice to export both constants and functions that work with
those constants (ex. the constants in the os, subprocess and re modules).

https://en.wikipedia.org/wiki/Enumerated_type
"""

# Possible sublist categories.
# Change the values as you see fit.
SUBLIST = 1
SUPERLIST = 2
EQUAL = 3
UNEQUAL = 0

def is_sublist(A: list, B: list) -> bool:
    """True if list_one is a contiguous slice in list_two"""

    lenA, lenB = len(A), len(B)
    if lenA == 0: 
        return True
    if lenA > lenB:
        return False
    return any(B[i:i+lenA] == A for i in range(lenB - lenA + 1))

def sublist(A:list, B:list):
    """
    return - relationship between lists A and B
    relation is one of 'equal', 'sublist', 'superlist', 'unequal'.
    """
    if A == B:
        return EQUAL
    elif is_sublist(A, B):
        return SUBLIST
    elif is_sublist(B, A):
        return SUPERLIST
    return UNEQUAL

```
