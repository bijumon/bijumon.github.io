"""Build static sites from Markdown and Djot documents.

The public classes are re-exported here for convenient use by tests and callers.
"""

from .builder import SiteBuilder
from .cache import FileCache
from .cli import main
from .converter import DocumentConverter
from .discovery import DocumentDiscovery
from .errors import BuildError
from .frontmatter import FrontmatterReader
from .indexer import FileIndexer
from .renderer import TemplateRenderer
from .reporter import Reporter

__all__ = [
    "BuildError",
    "DocumentConverter",
    "DocumentDiscovery",
    "FileCache",
    "FileIndexer",
    "FrontmatterReader",
    "Reporter",
    "SiteBuilder",
    "TemplateRenderer",
    "main",
]
