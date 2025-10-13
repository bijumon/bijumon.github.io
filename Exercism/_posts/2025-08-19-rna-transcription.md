---
date: Tue Aug 19 17:49:18 2025 +0530
---

``` python
"""
Determine the RNA complement of a given DNA sequence.
"""

def to_rna(dna_strand: str) -> str:
    result = []
    for strand in dna_strand:
        match strand:
            case "G":
                result.append("C")
            case "C":
                result.append("G")
            case "T":
                result.append("A")
            case "A":
                result.append("U")
    return "".join(result)
```