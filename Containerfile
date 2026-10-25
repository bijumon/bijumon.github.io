FROM docker.io/pandoc/core:latest

RUN apk add --no-cache uv python3

# Let uv install a compatible managed Python when the system Python is too old.
ENV UV_PYTHON_DOWNLOADS=automatic

WORKDIR /work
