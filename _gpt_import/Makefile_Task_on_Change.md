## user
In makefile howto run a task only if a file has changed
## assistant

In a Makefile, you can run a task only if a file has changed by using **Make's built-in dependency checking**. Make will only run a rule if the target file is out of date compared to its dependencies. Here’s a basic example:

```makefile
# Target file
output.txt: input.txt
    echo "File has changed, running task..." > output.txt
```

In this example:
- `output.txt` is the target file, and `input.txt` is its dependency.
- This rule will only run if `input.txt` has changed (i.e., if it has been modified more recently than `output.txt`).

### Explanation:
- If `input.txt` is newer than `output.txt`, or if `output.txt` does not exist, Make will run the recipe to create or update `output.txt`.
- If `input.txt` hasn't changed, Make will skip this rule.

### Advanced Usage: Force a Rule to Run Only When a Dependency Changes
If you need more complex conditions, you can use the `.PHONY` target to override behavior or check for file changes with shell commands within a recipe. However, the dependency-based approach above is typically the most efficient and straightforward.