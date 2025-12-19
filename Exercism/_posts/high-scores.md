---
date: Sun May 04 22:05:49 2025 +0530
---

``` python
"""
return the highest score from the list, the last added score and the three highest scores
"""

def latest(scores):
    return scores.pop()


def personal_best(scores):
    return max(scores)


def personal_top_three(scores):
    return sorted(scores, reverse=True)[:3]

```