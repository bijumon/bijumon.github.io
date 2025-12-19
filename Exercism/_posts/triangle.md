---
date: Tue May 20 11:03:16 2025 +0530
---

``` python
# Let a, b, and c be sides of the triangle. Then all three of the following expressions must be true:
#
# a + b ≥ c
# b + c ≥ a
# a + c ≥ b

def valid_triangle(sides):
    a,b,c = sides
    if (a+b >= c) and (b+c >= a) and (a+c >= b):
        return True
    else:
        return False

def equilateral(sides):
    a,b,c = sides
    if sum(sides) > 0 and valid_triangle(sides) and a == b == c:
        return True
    else:
        return False

def isosceles(sides):
    a,b,c = sides
    if sum(sides) > 0 and valid_triangle(sides) and (a == b or a == c or b == c or equilateral(sides)):
        return True
    else:
        return False

def scalene(sides):
    a,b,c = sides
    if sum(sides) > 0 and valid_triangle(sides) and (a != b and a != c and b != c):
        return True
    else:
        return False


```
