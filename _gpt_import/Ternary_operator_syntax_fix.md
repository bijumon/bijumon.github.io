## user
whats wrong 

 queue = express_queue if ticket_type == 1 else queue = normal_queue
## assistant

The issue with this line:

```python
queue = express_queue if ticket_type == 1 else queue = normal_queue
```

is **syntactic** — in Python, the ternary conditional operator has this syntax:

```python
value_if_true if condition else value_if_false
```

You should not repeat the variable name (`queue =`) inside the ternary expression. Here's the corrected version:

```python
queue = express_queue if ticket_type == 1 else normal_queue
```

### Breakdown:
- `ticket_type == 1` is the condition.
- `express_queue` is the value assigned if the condition is `True`.
- `normal_queue` is the value assigned if the condition is `False`.

Let me know if you want to add type hints or wrap this in a function!