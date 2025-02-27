# scalable-day-trading-system

### Updated setup using docker swarm

1. Initialize Docker Swarm
   `docker swarm init`

2. Build Docker Images

- `docker build -t daytrader-auth -f authentication/Dockerfile .`
- `docker build -t daytrader-transaction -f transaction/Dockerfile .`
- `docker build -t daytrader-database -f database/Dockerfile .`
- `docker build -t daytrader-matching-engine -f matching-engine/Dockerfile .`
- `docker build -t daytrader-api-gateway -f api-gateway/Dockerfile .`
- `docker build -t daytrader-frontend -f frontend/Dockerfile .`

3. Deploy the Docker Stack

- `docker stack deploy -c docker-stack.yml daytrader`

4. Verify Services are running

- `docker stack services daytrader`

### API Documentation

1. [Transaction Service](http://localhost:3001/transaction/docs)
2. [Authentication Service](http://localhost:3001/authentication/docs)
3. [Matching Engine Service](http://localhost:3001/engine/docs)
4. [Setup Service](http://localhost:3001/setup/docs)
