# scalable-day-trading-system

### Initial architecture / tech stack

#### Front End

- ReactJS

#### Reverse Proxy

- NGINX

#### Matching Engine

- FastAPI

#### Database

- PostgresDB

> Docker and Kubernetes

### Architecture Flow

Front End <--> Reverse Proxy <--> Matching Engine <--> Database

### Simplified flow for first deliverable

Front end container <--> Matching engine container <--> Database container

> Decouple services from the `Matching engine` container, and add the container managment + reverse proxy for a later deliverable
