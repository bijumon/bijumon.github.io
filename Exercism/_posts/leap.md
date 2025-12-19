---
date: Tue May 20 11:03:16 2025 +0530
---

``` python
def leap_year(year):
    # if year % 4 == 0 and year % 100 == 0 and year % 400 == 0:
    #     return True
    # elif year % 4 == 0 and not year % 100 == 0:
    #     return True
    # else:
    #     return False
    
    # year - 4 - 100 - 400
    # 1974   F   F     F    not
    # 1996   T   F     F    leap
    # 1960   T   F     F    leap
    # 1900   T   T     F    not
    # 2000   T   T     T    leap

    return year % 4 ==0 and (year % 100 !=0 or year % 400 == 0)

```
