---
date: 2025-08-11 08:54:26 +0530
---

``` python
"""
Determine if a number is perfect, abundant, or deficient
"""

import math

def classify(number: int) -> str:
    """ A perfect number equals the sum of its positive divisors.

    :param number: int a positive integer
    :return: str the classification of the input integer
    """
    if number <= 0:
        raise ValueError("Classification is only possible for positive integers.")
    elif number is 1:
        return "deficient"

    divisors = []
    for i in range(1, math.isqrt(number)+1):
        if number % i == 0:
            divisors.append(i)
            if i != 1 and i != number // i:
                divisors.append(number // i)

    sum_divisors = sum(divisors)
    if sum_divisors == number:
        return "perfect"
    elif sum_divisors > number:
        return "abundant"
    else:
        return "deficient"

```
