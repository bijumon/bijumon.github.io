## user
python check if string is empty
## assistant
In Python, you can check if a string is empty using a simple conditional statement. Here's how you can do it:

```python
# Method 1: Using if statement
my_string = ""
if my_string:
    print("String is not empty.")
else:
    print("String is empty.")

# Method 2: Using len() function
if len(my_string) == 0:
    print("String is empty.")
else:
    print("String is not empty.")
```

Both methods will output "String is empty." because an empty string evaluates to `False` in a boolean context.