# docker-build.ps1

# Initialize the swarm
docker swarm init

# Build all the services
$services = @("auth", "transaction", "database", "matching-engine", "api-gateway", "frontend")

foreach ($service in $services) {
    Write-Host "Building $service..."
    docker build -t "daytrader-$service" -f "$service/Dockerfile" .
}


# Deploy the swarm
docker stack deploy -c docker-stack.yml daytrader
