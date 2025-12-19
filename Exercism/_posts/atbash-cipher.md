---
date: Fri Aug 22 10:03:51 2025 +0530
---

``` python
"""
Implements Atbash cipher
"""

alphabets = "abcdefghijklmnopqrstuvwxyz"
cipher_map = str.maketrans(alphabets, alphabets[::-1])

def encode(plain_text: str) -> str:
    # Normalize and filter allowed characters
    filtered = "".join(ch.lower() for ch in plain_text if ch.isalpha() or ch.isdigit())
    
    # Translate alphabets using Atbash cipher
    translated = filtered.translate(cipher_map)
    
    # Insert spaces every 5 characters
    return " ".join(translated[i:i+5] for i in range(0, len(translated), 5))

def decode(ciphered_text):
    # Remove spaces, normalize case
    filtered = "".join(ch.lower() for ch in ciphered_text if ch.isalpha() or ch.isdigit())
    
    # Apply the Atbash mapping
    return filtered.translate(cipher_map)
```