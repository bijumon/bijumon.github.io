---
date: Tue Aug 19 13:40:04 2025 +0530
---

``` python
def rebase(input_base: int, digits: list[int], output_base: int) -> list[int]:
    """
    Convert a number from one base to another.

    input_base - The base of the input number (must be >= 2)
    digits - A list of integers representing the number in the input base
             Each digit must satisfy 0 <= digit < input_base
    output_base - The base to convert the number into (must be >= 2)

    returns - A list of integers representing the number in the output base.
        The most significant digit comes first

    raises - ValueError 
            if input_base or output_base < 2
            if any digit is out of range
    """

    if input_base < 2:
        raise ValueError("input base must be >= 2")
    if output_base < 2:
        raise ValueError("output base must be >= 2")
    
    if not digits or all(d == 0 for d in digits):
        return [0]
    
    if any(d < 0 or d >= input_base for d in digits):
        raise ValueError("all digits must satisfy 0 <= d < input base")
    
    # Convert digits to integer value
    value = 0
    for d in digits:
        value = value * input_base + d
    
    # Convert integer value to output_base
    result = []
    while value:
        value, rem = divmod(value, output_base)
        result.append(rem)
    
    return result[::-1]
```