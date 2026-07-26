.PHONY: serve build

serve:
	podman-compose run --rm --service-ports eleventy-serve

build:
	podman-compose run --rm eleventy-build
