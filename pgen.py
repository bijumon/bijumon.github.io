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
        template_filename = f"static/templates/{template}.jinja"
        if Path(template_filename).exists():
            print(f"using {template_filename} template")
            template_file = templates.environment.get_template(f"static/templates/{template}.jinja")
        else:
            print("using default template")
            template_file = templates.environment.get_template("static/templates/default.jinja")
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
    
