## user
in jekyll, i have 5 markdown files in chapters/ folder and I want to include the contents of each files in an index.html file
## assistant

To include the contents of multiple Markdown files from the `chapters/` folder into an `index.html` in Jekyll, you have a few options. Here's the most flexible and maintainable method using **[Jekyll includes](https://jekyllrb.com/docs/includes/)** or **a loop over site.pages or collections**, depending on how your chapters are set up.

---

### ✅ Option 1: Include files manually using `include`

This is simple if you have a fixed number of files and they don’t change often.

#### 1. Move your Markdown files to `_includes/chapters/`

Jekyll allows includes only from `_includes/`, so you'd move:

```
chapters/ch1.md → _includes/chapters/ch1.md
chapters/ch2.md → _includes/chapters/ch2.md
...
```

#### 2. In `index.html`, include them like this:

```html
---
layout: default
---

<h1>Chapters</h1>

{% include chapters/ch1.md %}
{% include chapters/ch2.md %}
{% include chapters/ch3.md %}
{% include chapters/ch4.md %}
{% include chapters/ch5.md %}
```

This will render the Markdown content from each file.

> ⚠️ Make sure each `.md` file in `_includes/chapters/` has **no front matter** (`---` lines at the top), or Jekyll will ignore them.

---

### ✅ Option 2: Use a [Collection](https://jekyllrb.com/docs/collections/) for dynamic chapter loading

This is best if you want to manage chapters more like a book structure.

#### 1. Define the collection in `_config.yml`:

```yaml
collections:
  chapters:
    output: false
```

#### 2. Move your files to `_chapters/`

```
_chapters/ch1.md
_chapters/ch2.md
...
```

Each file should have front matter like:

```markdown
---
title: "Chapter 1"
order: 1
---
Content here
```

#### 3. In `index.html`, loop over them:

```html
---
layout: default
---

<h1>Chapters</h1>

{% assign sorted_chapters = site.chapters | sort: "order" %}
{% for chapter in sorted_chapters %}
  <h2>{{ chapter.title }}</h2>
  {{ chapter.content }}
{% endfor %}
```

This automatically includes all chapters, sorted by `order`.

---

Which method suits you better — static or dynamic? I can help tailor it more if you tell me how your project is structured.