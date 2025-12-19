---
date: 2025-06-27 18:28:48 +0530
---

``` python
def square_root(n):
    """
    Calculates the square root of a number using the Babylonian method.

    Args:
        n: The number to find the square root of (must be non-negative).

    Returns:
        The approximate square root of n.
    """
    if n < 0:
        return "Square root is not defined for negative numbers."
    if n == 0:
        return 0

    guess = n / 2.0
    
    tolerance = 0.00001
    while abs(guess * guess - n) > tolerance:
        guess = (guess + n / guess) / 2.0
        
    return int(guess)

```
