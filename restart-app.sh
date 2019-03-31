#!/bin/bash
docker-compose down
docker-compose up -d
docker-compose run app
