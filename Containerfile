FROM docker.io/pandoc/core:latest

RUN apk add --no-cache uv python3

ENV UV_PYTHON_DOWNLOADS=never

WORKDIR /work
