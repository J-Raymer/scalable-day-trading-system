# build.sh
services=("authentication" "transaction" "database" "matching-engine" "api-gateway" "frontend")

for service in "${services[@]}"; do
  echo "Building $service..."
  docker build -t "daytrader-$service" -f "$service/Dockerfile" .
done
