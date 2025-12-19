---
date: 2025-07-28 20:59:16 +0530
---

``` python
"""
note: `pytest -s | --capture=no` shows print() output

start with a vowel, append "ay" at the end. 
starts with consonants, move to the end one by one until a vowel is found.
words beginning with "x" or "y" followed by a consonant, no further transformation.
keep the “u” attached to “q” when moving characters around

my -> ym -> ymay
square -> quares -> aresqu -> aresquay
yellow -> ellowy -> ellowyay
rhythm -> hythmr -> ythmrh -> ythmrhay
"""

vowels = ('a','e', 'i', 'o', 'u')


def pig_latin(word):

    # stages list stores intermediate transforms of the word
    stages = [word]
    
    while not word[0] in vowels:
        if word[0] in 'xy' and not word[1] in vowels:
            break
        word = word[1:] + word[0]
        if word[-1] == 'q' and word[0] == 'u':
            word = word[1:] + 'u'
        stages.append(word)
    
    stages.append(word+"ay")
    print(" -> ".join(stages))

    return word + 'ay'

def translate(sentence):
    return ' '.join([pig_latin(word) for word in sentence.split()])

```
