ifeq ($(shell command -v podman >/dev/null 2>&1 && echo yes),yes)
COMPOSE ?= podman compose
else
COMPOSE ?= docker compose
endif

.PHONY: build server

build:
	$(COMPOSE) run --rm build

server: build
	$(COMPOSE) run --rm --service-ports serve
