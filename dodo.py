from pathlib import Path
from doit import task

from pgen import Config, Content, Template

DOIT_CONFIG = {
    'backend': 'sqlite3',
    'dep_file': '.doit.sqlite'
}

def xconvert(config, input_file, output_file):
    with open(output_file, 'w') as f:
        f.write("test")

def task_convert():
    extensions = ['md', 'markdown', 'cmark']
    site_config = Config().load("config.toml")
    templates = Template(".")

    for ext in extensions:
        for input_file in Path(".").glob(f"**/*.{ext}"):
            output_file = input_file.with_suffix('.html')

            if not str(input_file) in site_config["ignore"]:
                content_file = Content(site_config, input_file)
                content_file.load(input_file)
                #content_file.convert(templates, output_file)
                
            yield {
                "name": str(input_file),
                "actions": [(content_file.convert, [templates, output_file])],
                "file_dep": [input_file],
                "targets": [output_file]
            }