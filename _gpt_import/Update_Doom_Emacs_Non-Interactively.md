## user
update doom emacs without being asked yes or no questions
## assistant

To update Doom Emacs **without being prompted with yes/no questions**, you can use the `--no-prompt` flag (or `--force` where applicable) with Doom's CLI tools.

Here’s a typical non-interactive update sequence:

```sh
doom sync --no-prompt
doom upgrade --no-prompt
doom build
```

Or, if you're scripting the update and want it fully unattended:

```sh
~/.emacs.d/bin/doom upgrade --no-prompt && \
~/.emacs.d/bin/doom sync --no-prompt && \
~/.emacs.d/bin/doom build
```

### Explanation:
- `doom upgrade --no-prompt`: Updates Doom Emacs and skips confirmation prompts.
- `doom sync --no-prompt`: Synchronizes Doom's config with no prompts.
- `doom build`: Recompiles packages; does not usually prompt but included for completeness.

### Note:
- These flags were added in newer versions of Doom Emacs. If you get an error that `--no-prompt` is unrecognized, try updating Doom manually once to ensure you have the latest CLI version.
- If using Doom with Git, consider wrapping it in a script that also updates your config repo.

Let me know if you're automating this or using a headless server—there may be extra steps.