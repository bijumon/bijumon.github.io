"""Read supported YAML and TOML frontmatter."""

from pathlib import Path
from typing import Any

import frontmatter
from frontmatter.default_handlers import TOMLHandler

from .errors import BuildError


class FrontmatterReader:
    """Read YAML (`---`) and TOML (`+++`) frontmatter."""

    def read(self, path: Path) -> tuple[dict[str, Any], str]:
        try:
            text = path.read_text(encoding="utf-8")
            lines = text.splitlines()
            first_line = lines[0].strip() if lines else ""

            if first_line in {"+++", "---"} and first_line not in lines[1:]:
                raise BuildError(
                    f"{path}: missing closing {first_line!r} frontmatter delimiter"
                )

            if first_line == "+++":
                post = frontmatter.loads(text, handler=TOMLHandler())
            elif first_line == "---":
                post = frontmatter.loads(text)
            else:
                return {}, text
        except BuildError:
            raise
        except Exception as exc:
            raise BuildError(f"{path}: cannot parse frontmatter: {exc}") from exc

        metadata = post.metadata
        if not isinstance(metadata, dict):
            raise BuildError(f"{path}: frontmatter must be a mapping of keys to values")
        return metadata, post.content
