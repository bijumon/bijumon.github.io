## user
in jekyll liquid template, show only pages with category 'pages'
## assistant

In a Jekyll Liquid template, you can filter and display only the pages with a specific category, such as "pages." Here's how you can do it:

```liquid
{% assign filtered_pages = site.pages | where: "category", "pages" %}

{% for page in filtered_pages %}
  <h2><a href="{{ page.url }}">{{ page.title }}</a></h2>
  <p>{{ page.content | strip_html | truncatewords: 30 }}</p>
{% endfor %}
```

### Explanation:
1. `site.pages` gives access to all pages.
2. `where: "category", "pages"` filters pages by category `"pages"`.
3. Inside the loop, `page.url`, `page.title`, and `page.content` provide the page’s link, title, and content respectively.

This will output a list of pages with the specified category.