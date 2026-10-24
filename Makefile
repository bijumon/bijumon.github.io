ifeq ($(shell command -v podman >/dev/null 2>&1 && echo yes),yes)
COMPOSE ?= podman compose
else
COMPOSE ?= docker compose
endif

.PHONY: build image serve

# Build the site (also ensure the container image exists and is current).
build: image
	$(COMPOSE) run --rm build

# Build the custom image defined by Containerfile.
image:
	$(COMPOSE) build build

# Build the site, then start the LiveReload server.
serve: build
	$(COMPOSE) run --rm --service-ports serve

# Run the tests for docbuild.py
test: 
	$(COMPOSE) run --rm test
