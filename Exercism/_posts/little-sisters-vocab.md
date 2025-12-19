---
date: Sun May 18 14:37:31 2025 +0530
---

``` python
"""Functions for creating, transforming, and adding prefixes to strings."""


def add_prefix_un(word):
    """Take the given word and add the 'un' prefix.

    :param word: str - containing the root word.
    :return: str - of root word prepended with 'un'.
    """

    return 'un' + word


def make_word_groups(vocab_words):
    """Transform a list containing a prefix and words into a string with the prefix followed by the words with prefix prepended.

    :param vocab_words: list - of vocabulary words with prefix in first index.
    :return: str - of prefix followed by vocabulary words with
            prefix applied.

    This function takes a `vocab_words` list and returns a string
    with the prefix and the words with prefix applied, separated
     by ' :: '.

    For example: list('en', 'close', 'joy', 'lighten'),
    produces the following string: 'en :: enclose :: enjoy :: enlighten'.
    """
    
    #prefix = vocab_words[0]
    #
    # create a list with prefix as first item,
    # append prefix to each work in list and add to list
    # words_with_prefix = [prefix + word for word in vocab_words[1:]]
    #
    # '[prefix]' is a list with only one item
    # return a string by joining '[prefix]' with list words_with_prefix
    # return ' :: '.join([prefix] + words_with_prefix)

    # above turned into a one-liner
    return ' :: '.join( [vocab_words[0]] + [vocab_words[0] + word for word in vocab_words[1:]] )



def remove_suffix_ness(word):
    """Remove the suffix from the word while keeping spelling in mind.

    :param word: str - of word to remove suffix from.
    :return: str - of word with suffix removed & spelling adjusted.

    For example: "heaviness" becomes "heavy", but "sadness" becomes "sad".
    """

    # word_root = word.split('ness')[0]
    word_root = word.removesuffix('ness')

    # if word_root[-1] == 'i':
    return word_root[:-1] + 'y' if word_root.endswith('i') else word_root
        


def adjective_to_verb(sentence, index):
    """Change the adjective within the sentence to a verb.

    :param sentence: str - that uses the word in sentence.
    :param index: int - index of the word to remove and transform.
    :return: str - word that changes the extracted adjective to a verb.

    For example, ("It got dark as the sun set.", 2) becomes "darken".
    """

    return sentence.strip('.').split()[index] + 'en'

```
