"""Command-line interface for docbuild."""

import argparse
import sys
from pathlib import Path

from .builder import SiteBuilder
from .errors import BuildError
from .reporter import Reporter


def main(argv: list[str] | None = None) -> int:
    """Parse command-line arguments and run a site build."""
    parser = argparse.ArgumentParser(
        description="Build Markdown and Djot files into _site/"
    )
    parser.add_argument(
        "source_dir",
        nargs="?",
        default=".",
        help="source directory (default: current working directory)",
    )
    args = parser.parse_args(argv)
    source = Path(args.source_dir).resolve()
    reporter = Reporter()
    if not source.is_dir():
        reporter.error("source directory does not exist: %s", source)
        return 2

    try:
        SiteBuilder(source, reporter=reporter).build()
    except (BuildError, OSError) as exc:
        reporter.error("%s", exc)
        return 1
    return 0
