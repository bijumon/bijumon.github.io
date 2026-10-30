"""Track static Jinja2 template dependencies for incremental builds."""

import hashlib

from jinja2 import Environment, meta
from jinja2.exceptions import TemplateError

from .errors import BuildError


class TemplateDependencyGraph:
    """Resolve template inheritance/includes and fingerprint their dependency closure.

    Edges point from a template to the templates it references. Dynamic
    references cannot be resolved safely before rendering, so their presence
    asks the caller to use a conservative whole-template-directory signature.
    """

    def __init__(self, environment: Environment) -> None:
        self.environment = environment
        self._sources: dict[str, str] = {}
        self._dependencies: dict[str, tuple[str, ...]] = {}
        self._dynamic: set[str] = set()
        self._signatures: dict[str, str | None] = {}

    def _load(self, name: str) -> tuple[tuple[str, ...], bool]:
        """Parse one template and cache its source and outgoing dependency edges."""
        if name in self._dependencies:
            return self._dependencies[name], name in self._dynamic

        loader = self.environment.loader
        if loader is None:
            raise BuildError("cannot inspect templates: no Jinja2 loader is configured")

        try:
            source, _, _ = loader.get_source(self.environment, name)
            syntax_tree = self.environment.parse(source)
        except (TemplateError, OSError, UnicodeError) as exc:
            raise BuildError(f"cannot inspect template {name!r}: {exc}") from exc

        dependencies: set[str] = set()
        dynamic = False
        for reference in meta.find_referenced_templates(syntax_tree):
            if reference is None:
                dynamic = True
            else:
                dependencies.add(reference)

        result = tuple(sorted(dependencies))
        self._sources[name] = source
        self._dependencies[name] = result
        if dynamic:
            self._dynamic.add(name)
        return result, dynamic

    def signature(self, template_name: str) -> str | None:
        """Return a stable signature, or None if a dynamic reference is present."""
        if template_name in self._signatures:
            return self._signatures[template_name]

        pending = [template_name]
        visited: set[str] = set()
        has_dynamic_reference = False

        while pending:
            current = pending.pop()
            if current in visited:
                continue
            visited.add(current)
            dependencies, dynamic = self._load(current)
            has_dynamic_reference = has_dynamic_reference or dynamic
            pending.extend(dependencies)

        if has_dynamic_reference:
            self._signatures[template_name] = None
            return None

        digest = hashlib.sha256()
        for name in sorted(visited):
            digest.update(name.encode("utf-8"))
            digest.update(b"\0")
            digest.update(self._sources[name].encode("utf-8"))
            digest.update(b"\0")

        signature = f"template-graph-v1:{digest.hexdigest()}"
        self._signatures[template_name] = signature
        return signature
