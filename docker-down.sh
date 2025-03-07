#!/usr/bin/bash

# Leave the swarm
docker swarm leave --force

# Nuke the volumes
docker volume rm daytrader_db_data
docker volume rm daytrader_redis_data

