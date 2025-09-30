############################################################
# INFRASTRUCTURE COMMANDS
.PHONY: up
## Start Docker compose containers
up: export DOCKER_BUILDKIT := 1
up: export COMPOSE_BAKE := true
up: export COMPOSE_DOCKER_CLI_BUILD=1
up:
	docker compose up


web-bash:
	docker compose run -u 0 --rm web /bin/bash
