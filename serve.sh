#!/bin/sh
set -eu

# LiveReload is installed for this invocation only; production builds do not
# depend on it and the project runtime dependencies remain unchanged.
exec uv run \
    --project /work/_src \
    --python /usr/bin/python3 \
    --with livereload \
    -- docbuild-serve /work \
        --host "${HOST:-0.0.0.0}" \
        --port "${PORT:-8000}" \
        --liveport "${LIVEPORT:-35729}"
