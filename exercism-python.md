+++
title = "python exercises from Exercism"
+++

["Hello, World!"](http://en.wikipedia.org/wiki/%22Hello,_world!%22_program) is the traditional first program for beginning programming in a new language or environment.

The objectives are simple:

- Write a function that returns the string "Hello, World!".
- Run the test suite and make sure that it succeeds.

``` python
def hello():
    return 'Hello, World!'
```

---

# Guido's Gorgeous Lasagna

You have five tasks, all related to cooking

1. Define expected bake time in minutes

Define an `EXPECTED_BAKE_TIME` constant that returns how many minutes the lasagna should bake in the oven.
According to your cookbook, the Lasagna should be in the oven for 40 minutes:

```python
>>> import lasagna
>>> lasagna.EXPECTED_BAKE_TIME
40
```

2. Calculate remaining bake time in minutes

Implement the `bake_time_remaining()` function that takes the actual minutes the lasagna has been in the oven as an argument and returns how many minutes the lasagna still needs to bake based on the `EXPECTED_BAKE_TIME`.

```python
>>> from lasagna import bake_time_remaining
>>> bake_time_remaining(30)
10
```

3. Calculate preparation time in minutes

Implement the `preparation_time_in_minutes()` function that takes the number of layers you want to add to the lasagna as an argument and returns how many minutes you would spend making them.
Assume each layer takes 2 minutes to prepare.

```python
>>> from lasagna import preparation_time_in_minutes
>>> preparation_time_in_minutes(2)
4
```

4. Calculate total elapsed cooking time (prep + bake) in minutes

Implement the `elapsed_time_in_minutes()` function that has two parameters: `number_of_layers` (_the number of layers added to the lasagna_) and `elapsed_bake_time` (_the number of minutes the lasagna has been baking in the oven_).
This function should return the total number of minutes you've been cooking, or the sum of your preparation time and the time the lasagna has already spent baking in the oven.

```python
>>> from lasagna import elapsed_time_in_minutes
>>> elapsed_time_in_minutes(3, 20)
26
```

5. Update the recipe with notes

Go back through the recipe, adding notes and documentation.

```python
def elapsed_time_in_minutes(number_of_layers, elapsed_bake_time):
    """
    Return elapsed cooking time.

    This function takes two numbers representing the number of layers & the time already spent 
    baking and calculates the total elapsed minutes spent cooking the lasagna.
    """
```

## Solution

``` python
"""Functions used in preparing Guido's gorgeous lasagna.

Learn about Guido, the creator of the Python language: https://en.wikipedia.org/wiki/Guido_van_Rossum
"""

EXPECTED_BAKE_TIME = 40

def bake_time_remaining(elapsed_bake_time):
    """Calculate the bake time remaining.
    :param elapsed_bake_time: int - baking time already elapsed.

    :return: int - remaining bake time (in minutes) derived from 'EXPECTED_BAKE_TIME'.

    Function that takes the actual minutes the lasagna has been in the oven as
    an argument and returns how many minutes the lasagna still needs to bake
    based on the `EXPECTED_BAKE_TIME`.
    """

    return EXPECTED_BAKE_TIME - elapsed_bake_time

def preparation_time_in_minutes(number_of_layers):
    """
    Return minutes spent making the recipe

    This function takes a number representing the number of layers added to the lasagne
    """

    preparation_time = 2
    return preparation_time * number_of_layers

def elapsed_time_in_minutes(number_of_layers, elapsed_bake_time):
    """
    Return elapsed cooking time.

    This function takes two numbers representing the number of layers & the time already spent 
    baking and calculates the total elapsed minutes spent cooking the lasagna.
    """

    return preparation_time_in_minutes(number_of_layers) + elapsed_bake_time
```

