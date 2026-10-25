"""Exceptions raised for expected, user-actionable build failures."""


class BuildError(Exception):
    """An actionable error that should stop the build."""
