---
date: 2025-06-27 18:27:39 +0530
---

``` python
"""
what will Bob reply to someone when they say something to him or ask him a question?
"""

def response(hey_bob: str):
    hey_bob = hey_bob.rstrip()
    if hey_bob.endswith("?"):
        if hey_bob.isupper():
            return "Calm down, I know what I'm doing!"
        else:
            return "Sure."
    elif hey_bob.isupper():
        return "Whoa, chill out!"
    elif hey_bob.isspace() or not hey_bob:
        return "Fine. Be that way!"
    else:
        return "Whatever."

```
