from markdown import markdown
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from toml import load as toml_load_from_file , loads as toml_load_from_str
from pprint import pprint

class Config:
    def load(self, config_file: Path) -> dict:
        with open(config_file, "r") as f:
            return toml_load_from_file(f)

class Content:
    def load(self,source_dir) -> list:
        items = []
        extensions = ['md', 'markdown', 'cmark']
        for ext in extensions:
            for content_file in Path(f"{source_dir}").glob(f"**/*.{ext}"):
                with open(content_file, 'r') as f:
                    frontmatter, text = f.read().split('+++',2)[1:]
                item = toml_load_from_str(frontmatter)
                
                if "title" not in item:
                    item["title"] = str(content_file.with_suffix('')) 
                item["content"] = markdown(text, extensions=['fenced_code', 'codehilite', 'tables'])
                item["slug"] = self.slugify(str(content_file.stem))
                item["url"] = str(content_file.with_suffix('.html'))
                if not "date" in item:
                    item["date"] = str(datetime.now())
                items.append(item)
                
        items.sort(key=lambda x: x["date"], reverse=True)
        return items

    # from https://www.30secondsofcode.org/python/s/slugify/
    def slugify(self, s):
        import re
        s = s.lower().strip()
        s = re.sub(r'[^\w\s-]', '', s)
        s = re.sub(r'[\s_-]+', '-', s)
        s = re.sub(r'^-+|-+$', '', s)
        return s

class Template:
    def load(self, template_directory: Path):
        return Environment(loader=FileSystemLoader(template_directory))

class Site:
    def __init__(self, config, content_items, template_directory: Path) -> None:

        pprint(config)
        templates = Template()
        environment = templates.load(template_directory)
        
        post_template = environment.get_template("post.jinja")
        for item in content_items["posts"]:
            with open(item["url"], "w") as output_file:
                output_file.write(post_template.render(site=config,post=item))
            output_file.close()
        
        post = { "title": "frontpage" } # remove, read from template header or generate
        index_template = environment.get_template("index.jinja")
        with open("index.html", "w") as index_file:
            index_file.write(index_template.render(posts=content_items,site=config,post=post))
        index_file.close()

if __name__ == '__main__':
    #config = Config()
    config = Config().load("config.toml")
    content = Content()
    content_items = { "posts": content.load(".") }
    #for i in content_items["posts"]: 
    #    for key, value in i.items():
    #        if key not in {"content"}:
    #            pprint(key + ' - ' + value)
    #    pprint("---")

    site = Site(config, content_items, ".")
