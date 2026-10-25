"""Build static sites from Markdown and Djot documents.

The public classes are re-exported here for convenient use by tests and callers.
"""

from .builder import SiteBuilder
from .cli import main
from .converter import DocumentConverter
from .discovery import DocumentDiscovery
from .errors import BuildError
from .frontmatter import FrontmatterReader
from .renderer import TemplateRenderer

__all__ = [
    "BuildError",
    "DocumentConverter",
    "DocumentDiscovery",
    "FrontmatterReader",
    "SiteBuilder",
    "TemplateRenderer",
    "main",
]
