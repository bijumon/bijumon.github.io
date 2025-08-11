## user
fedpkg build tutorial
## assistant

`fedpkg` is a command-line tool used by Fedora packagers to interact with Fedora's build systems (such as Koji and Bodhi) and Fedora Git repositories. If you want to build a package using `fedpkg`, here’s a basic tutorial to get you started.

---

### 🧰 Prerequisites

1. **Fedora Account** – Sign up at [accounts.fedoraproject.org](https://accounts.fedoraproject.org).
2. **Packaging Permissions** – You need to be a package maintainer to push and build packages officially.
3. **Install necessary tools:**

```bash
sudo dnf install fedpkg rpm-build redhat-rpm-config git
```

Optional but useful:
```bash
sudo dnf install mock koji rpmlint
```

---

### 🧪 Step-by-Step: Local Build

If you just want to build locally from a Fedora dist-git repo:

1. **Clone the package repo:**

```bash
fedpkg clone <package-name>
cd <package-name>
```

2. **Build locally with `fedpkg`:**

```bash
fedpkg local
```

This builds the RPMs using your local setup (`rpmbuild`), not in Koji or mock.

---

### 🛠 Step-by-Step: Koji Build (Official Fedora Build System)

To perform an official build:

1. **Set up Kerberos authentication:**

```bash
kinit your-fedora-username@FEDORAPROJECT.ORG
```

2. **Ensure you're on the correct branch (e.g., `rawhide`, `f39`, etc.):**

```bash
git checkout rawhide
```

3. **Make changes or update the `.spec` file as needed.**

4. **Commit changes:**

```bash
fedpkg commit -m "Update to version x.y.z"
```

5. **Push changes:**

```bash
fedpkg push
```

6. **Trigger a build in Koji:**

```bash
fedpkg build
```

This submits the build job to Koji.

---

### 🚀 Optional: Build for a Specific Target

You can also specify a target:

```bash
fedpkg build --target f39-build
```

Or test in a side tag:

```bash
fedpkg request-side-tag --base-tag f39-build
fedpkg build --target <side-tag>
```

---

### 🔍 Other Useful Commands

- Check the status of a build:
  ```bash
  koji watch-task <task-id>
  ```
- Scratch build (won’t be included in Fedora):
  ```bash
  fedpkg scratch-build
  ```

- Chain builds:
  ```bash
  fedpkg chain-build <pkg1> <pkg2>
  ```

---

### 📚 Resources

- Fedora Packaging Docs: https://docs.fedoraproject.org/en-US/packaging-guidelines/
- Koji Web UI: https://koji.fedoraproject.org/
- Pagure Fedora Git: https://src.fedoraproject.org/

---

Would you like an example using a specific package, or are you setting up a new one?
## user
fedpkg download source
## assistant
To **download the source** of a Fedora package using `fedpkg`, you can use the following command inside the package's git repository:

---

### 🧩 `fedpkg sources`

Once you've cloned the package repository, run:

```bash
fedpkg clone <package-name>
cd <package-name>
fedpkg sources
```

This will download the source tarballs (or other sources) listed in the `.spec` file and `sources` file, from the Fedora lookaside cache.

---

### Example:

```bash
fedpkg clone htop
cd htop
fedpkg sources
```

This will pull the `htop` source tarball (e.g., `htop-3.3.0.tar.gz`) into the current directory.

---

### 📝 Notes:

- If you just want to **look at the source code**, this is usually enough.
- The **`sources`** file contains checksums and names of the source files, and `fedpkg sources` uses that info to pull them from Fedora’s lookaside cache.
- If the `sources` file is missing or outdated, the command might fail. You can manually download the source and use `fedpkg new-sources` to upload it later if you are packaging.

---

Let me know if you want to fetch sources without cloning the whole repo, or if you're looking for the upstream (non-packaged) source instead.
## user
I have built a fedora package using 'fedpkg local' command, how do i build/upload it in copr using the rpm spec file. how can I build it for all current versions for fedora Linux?
## assistant

To build and upload your Fedora package to **[COPR](https://copr.fedorainfracloud.org/)** (Fedora's community build system), you can use your `.spec` file and source tarball (or SRPM). Here's a **step-by-step guide** to build and upload it to COPR for **all current Fedora releases**.

---

## ✅ Step-by-Step: Build & Upload to COPR

---

### 1. 🛠 Install COPR tools

```bash
sudo dnf install copr-cli
```

---

### 2. 🪪 Set up Authentication

Create a file at `~/.config/copr` with the following:

```ini
[copr-cli]
login = your_fedora_username
token = your_copr_token
```

Get your token from: https://copr.fedorainfracloud.org/api/

---

### 3. 📦 Prepare Your Package

You can upload either:
- An **SRPM** (`.src.rpm`)
- Or a **Git repo** with the `spec` file and sources

#### Option A: Build SRPM

If you've already used `fedpkg local`, you probably have the sources. To build an SRPM:

```bash
fedpkg srpm
```

This creates a `.src.rpm` file in the current directory.

---

### 4. 📤 Create a COPR Project (if not already)

```bash
copr-cli create your-copr-project-name \
  --chroot fedora-40-x86_64 \
  --chroot fedora-39-x86_64 \
  --chroot fedora-38-x86_64 \
  --description "My custom package"
```

(You can adjust or add `fedora-rawhide-x86_64` or other architectures as needed.)

---

### 5. 📦 Upload & Build

Now submit your `.src.rpm` to COPR:

```bash
copr-cli build your-username/your-copr-project-name yourpackage.src.rpm
```

Example:
```bash
copr-cli build biju/my-htop htop-3.3.0-1.fc40.src.rpm
```

This will trigger builds for all the selected Fedora versions in your project.

---

## 📝 Notes:

- If you want to **build from a Git repo** directly (e.g., from dist-git or personal project):

```bash
copr-cli build-package --name your-copr-project \
  --source-type git \
  --git-url https://src.fedoraproject.org/rpms/htop.git
```

- You can edit project settings at: https://copr.fedorainfracloud.org/coprs/your-username/your-copr-project/edit/

- Check your build status:
  ```bash
  copr-cli list-builds your-username/your-copr-project
  ```

---

## 🤖 Optional: Automate Build for Rawhide & New Releases

Use `--chroot fedora-rawhide-x86_64` or script builds when Fedora 41+ comes out.

---

Would you like a sample `copr-cli` config file and command prefilled for your package?
## user
Error: Operation requires API authentication
## assistant
The error:

```
Error: Operation requires API authentication
```

means that `copr-cli` is unable to authenticate with the COPR server. This usually happens when your API credentials are missing, misconfigured, or incorrect.

---

### ✅ Solution: Set Up COPR API Authentication

#### 🔑 Step 1: Get Your COPR API Token

1. Go to [COPR API tokens page](https://copr.fedorainfracloud.org/api/)
2. Log in with your Fedora account.
3. Generate a new token (if you haven’t already).
4. Copy both:
   - **Login** (your Fedora username)
   - **Token**

---

#### 📂 Step 2: Create or Edit Config File

Create a file called:

```bash
~/.config/copr
```

Add the following content:

```ini
[copr-cli]
login = your_fedora_username
token = your_api_token
```

🔐 Example:
```ini
[copr-cli]
login = biju
token = abcdef0123456789deadbeef
```

---

#### 🧪 Step 3: Test the Setup

```bash
copr-cli whoami
```

Expected output:
```
You are authenticated as: biju
```

---

### ✅ Tips

- Make sure the config file has **correct permissions**:
  ```bash
  chmod 600 ~/.config/copr
  ```
- No quotes around the token.
- No trailing spaces in the file.

---

Let me know if you’d like help writing a script to automate COPR builds for multiple Fedora versions.
## user
thanks. what can i do with copr-cli
## assistant
You're welcome! With `copr-cli`, you can **manage COPR projects**, **submit builds**, **monitor build status**, and more — all from the command line. Here's a breakdown of what you can do:

---

## 🚀 What You Can Do with `copr-cli`

---

### 📦 **Build Packages**

#### Build from SRPM:
```bash
copr-cli build <username/project> <path-to-src.rpm>
```

#### Build from Git:
```bash
copr-cli build-package --name <project> \
  --source-type git \
  --git-url <repo-url> \
  --git-branch <branch> \
  --spec <spec-file>
```

You can even set up auto-rebuilds on commits.

---

### 🔧 **Create or Modify Projects**

#### Create a new project:
```bash
copr-cli create myproject \
  --chroot fedora-40-x86_64 \
  --description "My personal build of htop"
```

#### Modify project settings:
```bash
copr-cli modify myproject --unlisted-on-hp true
```

---

### 🛠 **Manage Build Chroots**

Add chroots (e.g., Fedora versions):
```bash
copr-cli add-chroot myproject fedora-39-x86_64
```

Remove:
```bash
copr-cli remove-chroot myproject fedora-38-x86_64
```

---

### 🕵️ **Check Status of Builds**

#### List recent builds:
```bash
copr-cli list-builds <username/project>
```

#### Check single build status:
```bash
copr-cli get-build <build-id>
```

#### Cancel a build:
```bash
copr-cli cancel <build-id>
```

---

### 🌐 **Upload New Sources (lookaside cache)**

You can upload tarballs if needed:

```bash
copr-cli upload <username/project> file.tar.gz
```

Useful for `.spec` files that download from a source tarball.

---

### 🧪 **Trigger Rebuilds**

Rebuild last SRPM or Git for a specific chroot:

```bash
copr-cli rebuild <username/project> <build-id>
```

---

### 📃 **List Your Projects**

```bash
copr-cli list-projects
```

---

## 🧰 Other Features

- `copr-cli whoami` → Check current authentication
- `copr-cli delete-project <project>` → Delete a COPR project
- `copr-cli delete-build <build-id>` → Delete a specific build
- `copr-cli monitor <build-id>` → Live monitor build progress

---

## 📚 Documentation

- CLI help:
  ```bash
  copr-cli --help
  ```
- Full CLI manual:  
  [https://docs.pagure.org/copr.copr/copr-cli/](https://docs.pagure.org/copr.copr/copr-cli/)

---

Let me know if you'd like a **template script** to automate building and pushing packages to COPR for Rawhide + current Fedora releases!
## assistant
You're welcome! The `copr-cli` tool is powerful and lets you interact with [Fedora COPR](https://copr.fedorainfracloud.org/) from the command line. You can use it to **create projects, build packages, list builds, manage chroots**, and more.

Here’s a categorized overview of **what you can do with `copr-cli`**:

---

## 🛠️ Project Management

### ➕ Create a New Project

```bash
copr-cli create <project-name> --chroot fedora-40-x86_64 --description "My cool package"
```

### ⚙️ Modify an Existing Project

```bash
copr-cli modify <project-name> --unlisted-on-hp 1 --disable_createrepo 0
```

You can change:
- Description
- Chroots (build targets)
- Build options (Auto-rebuild, with/without mock, etc.)

### 🗑 Delete a Project

```bash
copr-cli delete <project-name>
```

---

## 📦 Package Builds

### 🚀 Build an SRPM

```bash
copr-cli build <project-name> path/to/package.src.rpm
```

You can build for selected chroots:
```bash
copr-cli build --nowait --chroot fedora-40-x86_64 <project-name> mypkg.src.rpm
```

### 🔄 Build from a Git Repo

```bash
copr-cli build-package --name <project-name> --source-type git \
  --git-url https://your.git.repo \
  --git-branch main
```

Optionally auto-enable monitoring of changes for rebuilds.

---

## 🧭 Query & Status

### 👤 Who Am I?

```bash
copr-cli whoami
```

### 📋 List Projects

```bash
copr-cli list
```

Or for another user:

```bash
copr-cli list biju
```

### 📦 List Packages in a Project

```bash
copr-cli list-packages <project-name>
```

### 🔍 List Builds in a Project

```bash
copr-cli list-builds <project-name>
```

Filter by status:

```bash
copr-cli list-builds <project-name> --state succeeded
```

---

## 🧹 Cleanup / Maintenance

### 🗑 Cancel Build

```bash
copr-cli cancel <build-id>
```

### 🧽 Delete All Builds (Be careful!)

```bash
copr-cli delete-builds <project-name> --before 2024-01-01
```

---

## 💡 Examples

### Create a project and upload an SRPM:
```bash
copr-cli create my-htop --chroot fedora-40-x86_64 --description "htop with patches"
copr-cli build my-htop ./htop-3.3.0-1.fc40.src.rpm
```

### Rebuild a failed build:
```bash
copr-cli rebuild my-htop 1234567
```

---

## 📚 Documentation

Official CLI doc:  
🔗 https://docs.pagure.org/copr.copr/copr-cli.html

---

Would you like a **template script** that automates project creation + SRPM build for all Fedora releases?