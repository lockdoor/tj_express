all: up

up:
	docker compose --env-file .env up -d 

down:
	docker compose down
	
build:
	docker compose build --no-cache
	docker compose --env-file .env up -d

.PHONY: all up down build