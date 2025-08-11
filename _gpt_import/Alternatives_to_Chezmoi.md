## user
suggest an alternative to chezmoi
## assistant

Here are some popular alternatives to **chezmoi** for dotfiles management, depending on your preferences for features, language, and workflow:

---

### 1. **yadm** (Yet Another Dotfiles Manager)
- **Language**: Bash
- **Pros**:
  - Git-based, no need for separate encryption tools.
  - Native support for encryption (via GPG).
  - Supports host-specific files, bootstrap script.
- **Use if**: You want something Git-native with minimal abstraction and GPG support.

📦: `sudo pacman -S yadm` or `brew install yadm`

---

### 2. **dotbot**
- **Language**: Python
- **Pros**:
  - Declarative config (YAML).
  - Focuses only on symlinking, but very extensible via scripts.
  - Easy to plug into existing dotfiles repos.
- **Use if**: You want a minimal, script-driven symlink manager without opinionated structure.

🔗: [https://github.com/anishathalye/dotbot](https://github.com/anishathalye/dotbot)

---

### 3. **rcm** (by Thoughtbot)
- **Language**: Shell
- **Pros**:
  - Simple toolset for managing dotfiles across multiple machines.
  - Works well with Git, custom hooks, and XDG paths.
- **Use if**: You want something simple and mature, used in production setups.

📦: `sudo pacman -S rcm` or `brew install rcm`

---

### 4. **homeshick**
- **Language**: Bash
- **Pros**:
  - Treats each dotfile as a separate Git repo ("castles").
  - Simple, effective, Git-based.
- **Use if**: You want to manage dotfiles modularly (e.g., per-app or per-purpose).

🔗: [https://github.com/andsens/homeshick](https://github.com/andsens/homeshick)

---

### 5. **stow** (GNU Stow)
- **Language**: Perl
- **Pros**:
  - Symlink farm manager (used for config management).
  - Unix-y philosophy, no abstraction.
- **Use if**: You prefer managing dotfiles in structured folders and want full manual control.

📦: `sudo pacman -S stow` or `brew install stow`

---

### Summary Table:

| Tool       | Encrypted Secrets | Git Integration | Declarative | Symlinks | Notes                        |
|------------|-------------------|------------------|-------------|----------|------------------------------|
| **chezmoi** | Yes (built-in)     | Yes              | Yes         | Yes      | Feature-rich, templating     |
| **yadm**    | Yes (GPG)          | Yes              | No          | Yes      | Git-centric                  |
| **dotbot**  | No                 | External         | Yes (YAML)  | Yes      | Easy to script               |
| **rcm**     | No (GPG optional)  | Yes              | No          | Yes      | Simple and portable          |
| **stow**    | No                 | External         | No          | Yes      | Classic Unix tool            |
| **homeshick** | No              | Yes              | No          | Yes      | Repo-per-set approach        |

---

Would you like a recommendation based on your usage pattern (e.g. encryption, templating, host-specific configs)?