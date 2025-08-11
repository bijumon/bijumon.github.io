## user
can i use handlebars or liquid as pandoc templates
## assistant

Yes, **Pandoc** uses a templating system, but it does **not** support **Handlebars** or **Liquid** templates directly. Instead, it has its **own template syntax** that is similar to Mustache, but simpler and more limited.

### ✅ Pandoc Template Language

Pandoc templates use:
- `{{variable}}` for inserting metadata.
- `$variable$` for inline variables.
- `$if(variable)$...$endif$` for conditional logic.
- `$for(list)$...$endfor$` for iteration.

This system is **not** as powerful as Liquid or Handlebars (no complex filters or logic), but it is sufficient for most document templating needs.

---

### ❌ You *cannot* use Handlebars or Liquid syntax directly

If you try to use `.hbs` or `.liquid` templates, Pandoc won’t understand the syntax and will either produce errors or pass the tags through as-is.

---

### ✅ Workarounds

If you want advanced templating like Liquid or Handlebars:
1. **Preprocess your markdown** with a templating engine (e.g., Jekyll for Liquid, or a Node.js tool for Handlebars).
2. **Then feed the result to Pandoc** for final conversion.

**Example workflow:**
```bash
# 1. Use Liquid via Jekyll or similar
jekyll build

# 2. Convert output with Pandoc
pandoc _site/mydoc.md -o mydoc.pdf
```

---

### Summary

| Feature                  | Pandoc Native | Handlebars / Liquid |
|--------------------------|----------------|----------------------|
| Variable substitution    | ✅              | ✅                    |
| Conditionals / Loops     | ✅ (basic)      | ✅ (advanced)         |
| Custom filters / helpers | ❌              | ✅                    |
| Direct support in Pandoc | ✅              | ❌                    |

Let me know if you want an example of a Pandoc template.
## user
is there a mustache implementation in haskell and can i use it with pandoc
## assistant
Yes, there **is a Mustache implementation in Haskell**, and you **can use it with Pandoc** — but **not directly as a Pandoc template**. Let’s break it down:

---

### ✅ Haskell Mustache Implementation

The Haskell library [`mustache`](https://hackage.haskell.org/package/mustache) provides a **compliant Mustache implementation**:

- Repository: [https://github.com/JustusAdam/mustache](https://github.com/JustusAdam/mustache)
- Install via Cabal or Stack:
  ```bash
  cabal install mustache
  ```

---

### ❌ Using Mustache *directly* with Pandoc

Pandoc does **not** natively support Mustache templates. Pandoc uses its own lightweight template engine (sometimes confused with Mustache due to similar syntax). Its system is **custom** and much more limited.

---

### ✅ How to *combine* Mustache with Pandoc

You can **preprocess your content using Mustache**, then pass the result to Pandoc. Here's how:

#### 1. Create a Mustache template:
```mustache
# mytemplate.mustache
Hello, {{name}}!

{{#items}}
- {{.}}
{{/items}}
```

#### 2. Preprocess with Haskell:
Write a small Haskell program to fill in the template using the `mustache` package.

#### 3. Pipe result into Pandoc:
```bash
runhaskell render.hs | pandoc -f markdown -t html -o output.html
```

#### 4. Alternative: Use Mustache to produce metadata
You can also use Mustache to build Pandoc metadata (YAML front matter), then feed it to Pandoc.

---

### ✅ Possible advanced use: Use Pandoc as a Haskell library

If you're writing a full Haskell program, you can:
- Parse a Markdown document using the `pandoc` library.
- Use `mustache` to generate additional content.
- Inject it into the Pandoc AST.
- Render the final document with Pandoc.

---

### Summary

| Goal                                | Supported? | How                          |
|-------------------------------------|------------|-------------------------------|
| Use Mustache as Pandoc template     | ❌         | Not supported                 |
| Use Mustache to preprocess content  | ✅         | Via Haskell or external tool  |
| Use Pandoc as a library with Mustache | ✅       | Full Haskell program          |

Let me know if you'd like a working example script that combines `mustache` and `pandoc` in Haskell.
## assistant
Yes, there **is** a Mustache implementation in Haskell, and you **can** use it alongside Pandoc — but not *inside* Pandoc’s native template system directly.

---

## ✅ Mustache in Haskell

There’s an official Mustache library for Haskell:

- **Library:** [`mustache`](https://hackage.haskell.org/package/mustache)
- **GitHub:** [https://github.com/JustusAdam/mustache](https://github.com/JustusAdam/mustache)
- Provides: parsing, rendering, partials, strict Mustache compliance

You can install it using Cabal or Stack:
```bash
cabal install mustache
# or
stack add mustache
```

---

## 🔧 Using Mustache with Pandoc

Pandoc **does not natively support Mustache** templates. However, you can use Mustache in **a preprocessing step**:

### ▶️ Workflow:
1. **Write your document** in Mustache-templated Markdown:
   ```markdown
   # Hello {{name}}

   You are reading a Mustache-preprocessed document.
   ```

2. **Render Mustache** using the Haskell library (or CLI tool like [mo](https://github.com/tests-always-included/mo) or a Node.js Mustache renderer).

3. **Feed the output to Pandoc**:
   ```bash
   ./render-mustache mydoc.mustache context.json > mydoc.md
   pandoc mydoc.md -o mydoc.pdf
   ```

---

## 🧠 When is this useful?

Using Mustache gives you:
- More powerful templates
- Reusable components
- External data sources (`.json`, `.yaml`)

If you’re generating many documents from structured data (like resumes, invoices, reports), Mustache + Pandoc is a solid combo.

---

## 🧪 Bonus: Combine with Haskell

If you're writing a Haskell program to automate this:

```haskell
import Text.Mustache
import qualified Data.Aeson as Aeson
import qualified Data.ByteString.Lazy as B

main :: IO ()
main = do
  template <- automaticCompile ["templates"] "mydoc.mustache"
  jsonData <- B.readFile "context.json"
  let context = Aeson.decode jsonData
  case template of
    Left err -> print err
    Right tpl -> case context of
      Nothing -> putStrLn "Invalid JSON"
      Just ctx -> putStrLn $ substitute tpl ctx
```

---

### 📝 Summary

| Feature                     | Supported |
|-----------------------------|-----------|
| Pandoc native Mustache      | ❌        |
| Haskell Mustache library    | ✅        |
| Mustache + Pandoc workflow  | ✅ (via pre-processing) |

Let me know if you’d like a minimal working Haskell + Mustache + Pandoc example.
## user
does pandoc support plugins and is there a plugin to use mustache as pandoc templates
## assistant
Pandoc does support **extensions** through two main mechanisms:

---

## ✅ 1. **Lua Filters** (Built-in Plugin System)
Pandoc has a **built-in plugin system** using **Lua filters**, which can manipulate the document AST (Abstract Syntax Tree) during conversion.

However, **Lua filters do not modify Pandoc templates**, which are used for final document layout (e.g., HTML, LaTeX, etc.). They operate on the **content** of the document, not the outer template system.

---

## ⚠️ 2. **Custom Writers or Preprocessing**  
Pandoc **does not natively support plugins for the template system** (i.e., no plug-and-play support to replace the native `$variable$` templating system with Mustache or Liquid).  

There is **no official Pandoc plugin** that lets you use **Mustache** as the template language for document rendering (like `--template my.mustache` using Mustache syntax). 

---

## 🔧 Workarounds

You **can** use Mustache by **preprocessing** the document and bypassing Pandoc's internal template system:

### ✅ Example Workflow: Use Mustache to render Markdown, then feed it to Pandoc

1. **Write Markdown with Mustache tags**:
   ```markdown
   # Hello, {{name}}
   Today is {{date}}.
   ```

2. **Render it with a Mustache engine** (Haskell, Node.js, or CLI):
   ```bash
   mustache context.json template.md > rendered.md
   ```

3. **Run Pandoc**:
   ```bash
   pandoc rendered.md -o output.pdf
   ```

---

## 🧠 Advanced Option: Build a Pandoc wrapper in Haskell

Since Pandoc is a Haskell library, you can write your own tool that:

- Loads a Mustache template
- Fills it with JSON/YAML data
- Feeds the result to Pandoc as Markdown
- Optionally writes a PDF, DOCX, etc.

---

## 🚫 Why Mustache as Pandoc Template Plugin Isn’t Possible

Pandoc templates are baked into how Pandoc formats output files like LaTeX, HTML, and DOCX. Their template system is designed for inserting metadata and controlling layout at the **document structure level**, not document **content**. Replacing this system with Mustache would require major internal changes.

---

## ✅ Summary

| Feature                                | Status     |
|----------------------------------------|------------|
| Native Mustache template support       | ❌          |
| Plugin to use Mustache in Pandoc       | ❌          |
| Lua filters for content transformation | ✅          |
| Preprocessing with Mustache (external) | ✅ ✅ ✅    |
| Write Haskell wrapper (Pandoc + Mustache) | ✅ (manual) |

Would you like a working CLI pipeline or Haskell example that integrates Mustache with Pandoc preprocessing?