# scalable-day-trading-system

### Updated setup using docker swarm

#### Suggested Run instructions

1. Run all services

`./docker-build.sh`

2. Clean up all services and volumes

`./docker-down.sh`

> All services and volumes must be cleared before running additional tests

#### Manual Run Instructions

1. Initialize Docker Swarm
   `docker swarm init`

2. Build Docker Images

- `docker build -t daytrader-auth -f auth/Dockerfile .`
- `docker build -t daytrader-transaction -f transaction/Dockerfile .`
- `docker build -t daytrader-database -f database/Dockerfile .`
- `docker build -t daytrader-matching-engine -f matching-engine/Dockerfile .`
- `docker build -t daytrader-api-gateway -f api-gateway/Dockerfile .`
- `docker build -t daytrader-frontend -f frontend/Dockerfile .`

3. **DO NOT SKIP THIS STEP** Load the environment variables from the .env file. This ONLY lasts in your current terminal
   if you close it and open another you'll have to pass this again.

- `export $(cat .env | xargs)`

4. Deploy the Docker Stack

- `docker stack deploy -c docker-stack.yml daytrader`

5. Verify Services are running

- `docker stack services daytrader`

6. Leaving the swarm

- `docker swarm leave --force`

7. Delete the volumes

- `docker volume rm daytrader_db_data`

#### Frontend

The frontend is hosted at [localhost:5763](http://localhost:5173)

### API Documentation

1. [Transaction Service](http://localhost:3001/transaction/docs)
2. [Authentication Service](http://localhost:3001/authentication/docs)
3. [Matching Engine Service](http://localhost:3001/engine/docs)
4. [Setup Service](http://localhost:3001/setup/docs)
