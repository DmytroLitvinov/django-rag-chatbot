############################################################
# INFRASTRUCTURE COMMANDS
.PHONY: up
## Start Docker compose containers
up: export DOCKER_BUILDKIT := 1
up: export COMPOSE_BAKE := true
up: export COMPOSE_DOCKER_CLI_BUILD=1
up:
	docker compose up

.PHONY: rebuild
## Rebuild 'app' container in case something went wrong
rebuild: export DOCKER_BUILDKIT := 1
rebuild: export COMPOSE_BAKE := true
rebuild: export COMPOSE_DOCKER_CLI_BUILD=1
rebuild:
	docker compose down
	docker compose build

web-bash:
	docker compose run -u 0 --rm web /bin/bash
