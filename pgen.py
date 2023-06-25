from markdown import markdown
from datetime import datetime
from dataclasses import dataclass
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from toml import load as toml_load_from_file , loads as toml_load_from_str
from pprint import pprint


class Config:
    def load(self, config_file: Path) -> dict:
        with open(config_file, "r") as f:
            return toml_load_from_file(f)

class Template:
    def __init__(self, template_directory):
        self.environment = self.load(template_directory)

    def load(self, template_directory: Path):
        return Environment(loader=FileSystemLoader(template_directory))

class Content:
    def __init__(self, config: Config, input_file: Path) -> None:
        self.filename = input_file
        self.config = config
        self.frontmatter: dict = {}
        self.content: str = ""

    def load(self,input_file):
        with open(input_file, 'r') as f:
            metadata, text = f.read().split('+++',2)[1:]
            self.frontmatter = toml_load_from_str(metadata)
        self.content = self.parse(text)
        self.defaults()
    
    def defaults(self):
        if "title" not in self.frontmatter:
            self.frontmatter["title"] = self.slugify(str(self.filename.stem))
        if not "url" in self.frontmatter:    
            self.frontmatter["url"] = str(self.filename.with_suffix('.html'))
        if not "date" in self.frontmatter:
            self.frontmatter["date"] = str(datetime.now())
        if not "layout" in self.frontmatter:
            self.frontmatter["layout"] = "post"
    
    def parse(self, text: str):
        return markdown(text, extensions=['fenced_code', 'codehilite', 'tables'])
    
    def convert(self,templates: Template, output_file):
        #print(self.frontmatter)
        template = self.frontmatter["layout"]
        template_filename = f"{template}.jinja"
        if Path(template_filename).exists():
            print(f"using {template_filename} template")
            template_file = templates.environment.get_template(f"{template}.jinja")
        else:
            print("using default template")
            template_file = templates.environment.get_template("default.jinja")
        self.frontmatter["content"] = self.content
        with open(output_file, "w") as f:
            f.write(template_file.render(site=self.config,post=self.frontmatter))

    # from https://www.30secondsofcode.org/python/s/slugify/
    def slugify(self, s):
        import re
        s = s.lower().strip()
        s = re.sub(r'[^\w\s-]', '', s)
        s = re.sub(r'[\s_-]+', '-', s)
        s = re.sub(r'^-+|-+$', '', s)
        return s
    
    def old_load(self,source_dir) -> list:
        items = []
        extensions = ['md', 'markdown', 'cmark']
        for ext in extensions:
            for content_file in Path(f"{source_dir}").glob(f"**/*.{ext}"):
                if not str(content_file) in self.config["ignore"]:
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
    
class Site:
    def convert(self, config, content_items, template_directory: Path) -> None:
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
    extensions = ['md', 'markdown', 'cmark']
    site_config = Config().load("config.toml")
    templates = Template(".")

    for ext in extensions:
        for input_file in Path(".").glob(f"**/*.{ext}"):
            output_file = input_file.with_suffix('.html')

            if not str(input_file) in site_config["ignore"]:
                content_file = Content(site_config, input_file)
                content_file.load(input_file)
                content_file.convert(templates, output_file)
