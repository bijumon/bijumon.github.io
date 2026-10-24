#!/bin/sh
set -eu

mkdir -p _site

exec uv run \
    --python /usr/bin/python3 \
    --with livereload \
    -- livereload \
        --host 0.0.0.0 \
        --port 8000 \
        _site
