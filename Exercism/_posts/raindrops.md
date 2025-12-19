---
date: Thu May 01 22:53:09 2025 +0530
---

``` python
""" 
Raindrops is a slightly more complex version of the FizzBuzz challenge, a classic interview question. 
Convert a number into its corresponding raindrop sounds.
"""

def convert(number):
    answer = []
    raindrops = {3:"Pling", 5:"Plang", 7:"Plong"}
    
    if number % 3 == 0:
        answer += raindrops[3]
    if number % 5 == 0:
        answer += raindrops[5]
    if number % 7 == 0:
        answer += raindrops[7]
    return ''.join(answer) or str(number)
```