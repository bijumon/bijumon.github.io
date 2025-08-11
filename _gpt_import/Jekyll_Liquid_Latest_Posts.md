## user
in jekyll liquid, show all posts belonging to 'latest' tag
## assistant

To display all posts with the `latest` tag in Jekyll using Liquid, you can loop through all the posts and filter those that have the `latest` tag.

Here’s how you can do it in your template:

```liquid
{% for post in site.posts %}
  {% if post.tags contains 'latest' %}
    <article>
      <h2><a href="{{ post.url }}">{{ post.title }}</a></h2>
      <p>{{ post.excerpt }}</p>
      <p><small>Posted on {{ post.date | date: "%B %d, %Y" }}</small></p>
    </article>
  {% endif %}
{% endfor %}
```

### Explanation:
- `site.posts`: Contains all the posts in your Jekyll site.
- `post.tags contains 'latest'`: Filters posts that include the `latest` tag.
- Inside the loop, you can display each post’s title, URL, excerpt, and date as desired.

You can customize the layout or add more details as necessary for your site!