COMPOSE ?= docker compose

.PHONY: build server

build:
	$(COMPOSE) run --rm build

server: build
	$(COMPOSE) run --rm --service-ports serve
