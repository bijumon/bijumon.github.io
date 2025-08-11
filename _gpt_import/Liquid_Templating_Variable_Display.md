## user
in liquid templating language, display a variable page.title if it is not empty
## assistant

In Liquid templating, you can display a variable only if it is not empty using an `{% if %}` conditional. Here’s how you can display `page.title` only if it has a value:

```liquid
{% if page.title != blank %}
  {{ page.title }}
{% endif %}
```

This code checks if `page.title` is not empty or blank, and if it's not, it outputs `page.title`.
## assistant

In Liquid templating, you can display a variable like `page.title` if it is not empty by using an `if` statement. Here’s how:

```liquid
{% if page.title %}
  {{ page.title }}
{% endif %}
```

This will check if `page.title` has a value (i.e., it's not empty or `nil`) and then display it if it does.
## user
in jekyll, show list of tags in liquid
## assistant
In Jekyll, to display a list of tags for a post, you can use the Liquid templating language to loop through the tags. Assuming each post has a `tags` field (an array of tags), you can do this:

```liquid
{% if page.tags %}
  <ul>
    {% for tag in page.tags %}
      <li>{{ tag }}</li>
    {% endfor %}
  </ul>
{% endif %}
```

This will display each tag in a list format. You can also apply this loop to a collection of posts to show all unique tags in your Jekyll site. Here’s an example of how you can display all unique tags across all posts:

```liquid
{% assign all_tags = "" | split: "" %}
{% for post in site.posts %}
  {% assign all_tags = all_tags | concat: post.tags %}
{% endfor %}

{% assign unique_tags = all_tags | uniq %}

<ul>
  {% for tag in unique_tags %}
    <li>{{ tag }}</li>
  {% endfor %}
</ul>
```

This code loops through each post, collects all tags, removes duplicates with `uniq`, and then displays them in a list.