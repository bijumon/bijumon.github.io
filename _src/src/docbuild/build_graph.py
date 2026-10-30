"""Represent build inputs, virtual dependencies, and generated outputs."""

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .errors import BuildError


@dataclass(frozen=True)
class GraphNode:
    """One source, virtual, template, or output node."""

    key: str
    kind: str
    signature: str


@dataclass(frozen=True)
class BuildArtifact:
    """The persisted state of one output that can be considered for rebuilding."""

    node_key: str
    destination: Path
    built_signature: str | None
    exists: bool


@dataclass(frozen=True)
class BuildTask:
    """A planned output operation and the effective signature to persist on success."""

    node_key: str
    destination: Path
    signature: str
    reason: str


@dataclass(frozen=True)
class BuildPlan:
    """Outputs that need work and outputs that are already up to date."""

    tasks: tuple[BuildTask, ...]
    unchanged: tuple[BuildArtifact, ...]


class BuildGraph:
    """Small directed acyclic graph used to calculate effective input signatures.

    A node's effective signature includes its own signature and the effective
    signatures of every dependency. The edge direction is expressed as
    node depends on dependency.
    """

    def __init__(self) -> None:
        self._nodes: dict[str, GraphNode] = {}
        self._dependencies: dict[str, set[str]] = {}

    def add_node(self, key: str, kind: str, signature: str) -> None:
        """Add a node, rejecting conflicting definitions for the same key."""
        node = GraphNode(key=key, kind=kind, signature=signature)
        previous = self._nodes.get(key)
        if previous is not None and previous != node:
            raise BuildError(f"conflicting build graph node definition: {key}")
        self._nodes[key] = node
        self._dependencies.setdefault(key, set())

    def depends_on(self, node_key: str, dependency_key: str) -> None:
        """Record that node_key consumes dependency_key."""
        if node_key not in self._nodes:
            raise BuildError(f"unknown build graph node: {node_key}")
        if dependency_key not in self._nodes:
            raise BuildError(f"unknown build graph dependency: {dependency_key}")
        self._dependencies[node_key].add(dependency_key)

    def dependencies(self, node_key: str) -> tuple[str, ...]:
        """Return a stable list of direct dependencies for one node."""
        if node_key not in self._nodes:
            raise BuildError(f"unknown build graph node: {node_key}")
        return tuple(sorted(self._dependencies[node_key]))

    def signature(self, node_key: str) -> str:
        """Calculate a deterministic signature across the complete dependency closure."""
        memo: dict[str, str] = {}
        visiting: list[str] = []

        def resolve(key: str) -> str:
            cached = memo.get(key)
            if cached is not None:
                return cached
            node = self._nodes.get(key)
            if node is None:
                raise BuildError(f"unknown build graph node: {key}")
            if key in visiting:
                cycle_start = visiting.index(key)
                cycle = " -> ".join([*visiting[cycle_start:], key])
                raise BuildError(f"dependency cycle detected: {cycle}")

            visiting.append(key)
            digest = hashlib.sha256()
            digest.update(node.kind.encode("utf-8"))
            digest.update(b"\0")
            digest.update(node.key.encode("utf-8"))
            digest.update(b"\0")
            digest.update(node.signature.encode("utf-8"))
            digest.update(b"\0")
            for dependency_key in sorted(self._dependencies[key]):
                digest.update(dependency_key.encode("utf-8"))
                digest.update(b"\0")
                digest.update(resolve(dependency_key).encode("ascii"))
                digest.update(b"\0")
            visiting.pop()

            result = f"build-graph-v1:{digest.hexdigest()}"
            memo[key] = result
            return result

        return resolve(node_key)


class BuildPlanner:
    """Compare effective graph signatures with persisted output signatures."""

    def plan(
        self,
        graph: BuildGraph,
        artifacts: Iterable[BuildArtifact],
    ) -> BuildPlan:
        """Return build tasks for missing or stale outputs."""
        tasks: list[BuildTask] = []
        unchanged: list[BuildArtifact] = []

        for artifact in artifacts:
            current_signature = graph.signature(artifact.node_key)
            if not artifact.exists:
                reason = "missing output"
            elif artifact.built_signature is None:
                reason = "no previous graph signature"
            elif artifact.built_signature != current_signature:
                reason = "dependency changed"
            else:
                unchanged.append(artifact)
                continue

            tasks.append(
                BuildTask(
                    node_key=artifact.node_key,
                    destination=artifact.destination,
                    signature=current_signature,
                    reason=reason,
                )
            )

        return BuildPlan(tasks=tuple(tasks), unchanged=tuple(unchanged))
