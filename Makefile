export EXPRESS_PATH := ExpressI
export COMPANIES := {"TJ":"TJ69","TJ68":"TJ68","THAIJINTAN":"JINTAN68","RINARA":"RINARA68"}
export PORT := 8001
export HOST := 0.0.0.0
export IS_CONTAINER := TRUE
export SERVERS_PATH := ./asset_dev/ExpressI

all: up

up:
	docker compose up -d

down:
	docker compose down
	
build:
	docker compose build --no-cache
	docker compose up -d

.PHONY: all up down build