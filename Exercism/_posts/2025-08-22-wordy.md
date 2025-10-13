---
date: Fri Aug 22 10:04:16 2025 +0530
---

``` python
"""
Parse and evaluate simple math word problems returning the answer as an integer.
"""

def answer(question: str) -> int:
    replacements = {
        "What is": "",
        "plus": "+",
        "minus": "-",
        "multiplied by": "*",
        "divided by": "/",
        "?": ""
    }

    for word, symbol in replacements.items():
        question = question.replace(word, symbol)

    tokens = question.split()
    tokens.insert(0, "(")
    tokens.insert(4, ")")

    if len(tokens) < 3:
        raise ValueError("syntax error")
    
    if any(token.isalpha() and token not in list(replacements.keys()) for token in tokens):
        raise ValueError("unknown operation")

    try:
        return eval(" ".join(tokens))
    except:
        raise ValueError("syntax error")

```