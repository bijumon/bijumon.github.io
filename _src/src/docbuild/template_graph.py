"""Track static Jinja2 template dependencies for incremental builds."""

import hashlib

from jinja2 import Environment, meta, nodes
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
        self._site_pages: dict[str, bool] = {}
        self._site_metadata_keys: dict[str, frozenset[str] | None] = {}

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
        site_metadata_keys, uses_site_pages = self._site_references(syntax_tree)
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
        self._site_pages[name] = uses_site_pages
        self._site_metadata_keys[name] = site_metadata_keys
        return result, dynamic

    @staticmethod
    def _site_references(
        syntax_tree: nodes.Template,
    ) -> tuple[frozenset[str] | None, bool]:
        """Find statically identifiable site metadata keys and catalog use.

        A None key set means the template may inspect the site mapping
        dynamically, so every metadata key is treated as a dependency. Dynamic
        or indirect uses also conservatively depend on site.pages.
        """
        metadata_keys: set[str] = set()
        uses_site_pages = False
        all_metadata = False
        mapping_methods = {
            "get", "items", "keys", "values", "copy", "update", "pop", "setdefault"
        }

        def visit(node: nodes.Node) -> None:
            nonlocal uses_site_pages, all_metadata
            for child in node.iter_child_nodes():
                if isinstance(child, nodes.Name) and child.name == "site":
                    if isinstance(node, nodes.Getattr) and node.node is child:
                        if node.attr == "pages":
                            uses_site_pages = True
                        elif node.attr in mapping_methods:
                            all_metadata = True
                            uses_site_pages = True
                        else:
                            metadata_keys.add(node.attr)
                    elif isinstance(node, nodes.Getitem) and node.node is child:
                        if isinstance(node.arg, nodes.Const):
                            key = node.arg.value
                            if key == "pages":
                                uses_site_pages = True
                            elif isinstance(key, str):
                                metadata_keys.add(key)
                            else:
                                all_metadata = True
                                uses_site_pages = True
                        else:
                            all_metadata = True
                            uses_site_pages = True
                    else:
                        # Aliases, filters, tests, and other indirect access
                        # can expose any key in the site mapping.
                        all_metadata = True
                        uses_site_pages = True
                visit(child)

        visit(syntax_tree)
        return (None if all_metadata else frozenset(metadata_keys), uses_site_pages)

    def site_dependencies(
        self, template_name: str
    ) -> tuple[frozenset[str] | None, bool]:
        """Return (metadata keys, uses site.pages) for a template dependency closure.

        A None metadata-key set means all site metadata is relevant. Dynamic
        includes are conservative because their contents cannot be inspected.
        """
        metadata_keys: set[str] = set()
        all_metadata = False
        uses_site_pages = False
        pending = [template_name]
        visited: set[str] = set()

        while pending:
            current = pending.pop()
            if current in visited:
                continue
            visited.add(current)
            dependencies, dynamic = self._load(current)
            current_keys = self._site_metadata_keys[current]
            if dynamic or current_keys is None:
                all_metadata = True
                uses_site_pages = True
            else:
                metadata_keys.update(current_keys)
            uses_site_pages = uses_site_pages or self._site_pages[current]
            pending.extend(dependencies)

        return (None if all_metadata else frozenset(metadata_keys), uses_site_pages)

    def dependency_nodes(
        self, template_name: str
    ) -> dict[str, tuple[str, tuple[str, ...]]] | None:
        """Return source signatures and edges for the static template closure.

        Each mapping value contains a template-content SHA-256 digest and the
        names of templates it directly references. None indicates a dynamic
        reference, for which the caller must use the conservative all-templates
        virtual node instead.
        """
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
            return None

        result: dict[str, tuple[str, tuple[str, ...]]] = {}
        for name in sorted(visited):
            source = self._sources[name]
            digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
            result[name] = (digest, self._dependencies[name])
        return result

    def uses_site_pages(self, template_name: str) -> bool:
        """Return whether a template or any static dependency reads site.pages."""
        return self.site_dependencies(template_name)[1]

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
