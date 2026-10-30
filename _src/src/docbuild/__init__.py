"""Build static sites from Markdown and Djot documents.

The public classes are re-exported here for convenient use by tests and callers.
"""

from .builder import SiteBuilder
from .build_graph import BuildArtifact, BuildGraph, BuildPlan, BuildPlanner, BuildTask
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
    "BuildArtifact",
    "BuildError",
    "BuildGraph",
    "BuildPlan",
    "BuildPlanner",
    "BuildTask",
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
