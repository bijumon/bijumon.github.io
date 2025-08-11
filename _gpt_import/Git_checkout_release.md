## user
git checkout a release
## assistant

To check out a **release** in Git, you generally want to check out a specific **tag** (used for releases) or **branch**. Here’s how:

---

### 🔹 **1. List All Releases (Tags)**
Most releases are tagged. To see them:

```bash
git fetch --tags
git tag
```

This lists all tags, such as `v1.0.0`, `release-2025.07`, etc.

---

### 🔹 **2. Checkout a Release Tag**

```bash
git checkout tags/<tag-name>
```

Example:

```bash
git checkout tags/v1.2.0
```

> This puts you in a **detached HEAD** state (read-only; not on a branch).

---

### 🔹 **3. (Optional) Create a Branch from That Release**

If you want to make changes or stay on that code:

```bash
git checkout -b my-release-branch tags/v1.2.0
```

---

### 🔹 **4. Alternatively: Checkout a Release Branch**

If the project has a release branch (e.g. `release/1.2`), use:

```bash
git checkout release/1.2
```

---

Let me know if you need help checking out a GitHub release or building from it.