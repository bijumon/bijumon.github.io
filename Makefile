ifeq ($(shell command -v podman >/dev/null 2>&1 && echo yes),yes)
COMPOSE ?= podman compose
else
COMPOSE ?= docker compose
endif

.PHONY: build image serve test

# Build the site (also ensure the container image exists and is current).
build: image
	$(COMPOSE) run --rm build

# Build the custom image defined by Containerfile.
image:
	$(COMPOSE) build build

# Build once, then serve and incrementally rebuild through docbuild-serve.
# Do not depend on "build": the development server owns its initial build.
serve:
	$(COMPOSE) run --rm --service-ports serve

# Run the docbuild test suite.
test:
	$(COMPOSE) run --rm test
