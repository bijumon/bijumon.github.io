from pathlib import Path
from doit import task

from pgen import Config, Content, Template

DOIT_CONFIG = {
    'backend': 'sqlite3',
    'dep_file': '.doit.sqlite'
}

site_config = Config().load("config.toml")
templates = Template(".")
items = []

def task_convert():
    extensions = ['md', 'markdown', 'cmark']
    for ext in extensions:
        for input_file in Path(".").glob(f"**/*.{ext}"):
            content_item = {}
            output_file = input_file.with_suffix('.html')

            if not str(input_file) in site_config["ignore"]:
                content_file = Content(site_config, input_file)
                content_file.load(input_file)
                content_item["content"] = content_file.content
                content_item.update(content_file.frontmatter)
                items.append(content_item)
                
            yield {
                "name": str(input_file),
                "actions": [(content_file.convert, [templates, output_file])],
                "file_dep": [input_file],
                "targets": [output_file]
            }

def build_index():
    post = { "title": "frontpage" }
    items.sort(key=lambda x: x["date"], reverse=True)
    content_items = { "posts" : items }
    index_template = templates.environment.get_template("index.jinja")
    with open("index.html", "w") as index_file:
        index_file.write(index_template.render(posts=content_items,site=site_config,post=post))

def task_build_index():
    yield {
        "name": "build index",
        "actions": [(build_index)],
        "targets": ["index.html"]
    }
