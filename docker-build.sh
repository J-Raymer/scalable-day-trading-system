# build.sh

# Initialize the swarm
docker swarm init

# Build all the services
services=("auth" "transaction" "database" "matching-engine" "api-gateway" "frontend")

for service in "${services[@]}"; do
  echo "Building $service..."
  docker build -t "daytrader-$service" -f "$service/Dockerfile" .
done

# Load environment variables from .env file
export $(cat .env | xargs)

# Deploy the swarm
docker stack deploy -c docker-stack.yml daytrader
