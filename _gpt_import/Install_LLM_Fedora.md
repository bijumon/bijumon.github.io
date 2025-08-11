## user
how do i get the llm command in fedora
## assistant

To get the `llm` command on **Fedora**, you're probably referring to the [llm CLI tool](https://github.com/simonw/llm) by Simon Willison, which lets you interact with local or remote large language models via the terminal.

Here's how to install it on **Fedora**:

---

### 🔧 Step-by-Step Installation

#### 1. **Ensure Python is installed**
Fedora ships with Python 3 by default, but just in case:

```bash
python3 --version
```

#### 2. **Install `llm` using pip**
You can install it with:

```bash
pip install llm
```

> If you don't have `pip`, install it with:
> ```bash
> sudo dnf install python3-pip
> ```

---

### ✅ Verifying installation

```bash
llm --help
```

You should see the command-line help.

---

### 🧠 Optional: Add a model (e.g., OpenAI or local model)

#### Example for OpenAI:

```bash
llm keys set openai YOUR_OPENAI_API_KEY
```

#### Or to use **local models** like `llama.cpp`:

```bash
llm install llm-llama-cpp
```

Then point it to your local model:

```bash
llm llama-cpp add path-to-your-model.gguf
```

---

Let me know if you’re trying to use it with a specific model (like OpenAI, LLaMA, Mistral, etc.) or locally on CPU/GPU—can help you set that up too.