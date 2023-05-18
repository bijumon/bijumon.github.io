
class Config:
    def __init__(self) -> None:
        pass

class Content:
    def __init__(self) -> None:
        pass

class Template:
    def __init__(self) -> None:
        pass

class Site:
    def __init__(self, config, content, templates) -> None:
        pass

if __name__ == '__main__':
    config = Config()
    content = Content()
    templates = Template()
    site = Site(config, content, templates)
