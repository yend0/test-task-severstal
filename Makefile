DC = docker compose
PRUNE = docker system prune

DOCKER_COMPOSE_FILE_PATH = etc/infra/docker-compose.yaml

.PHONY: start
start:
	${DC} -f ${DOCKER_COMPOSE_FILE_PATH} up --build -d

.PHONY: drop
drop:
	${DC} -f ${DOCKER_COMPOSE_FILE_PATH}  down

.PHONY: prune
prune:
	${PRUNE} -a

.PHONY: start-services
start-services:
	@echo "Specify services to start with SERVICES variable, e.g., make start-services SERVICES='service1 service2'"
	${DC} -f ${DOCKER_COMPOSE_FILE_PATH} up --build -d ${SERVICES}