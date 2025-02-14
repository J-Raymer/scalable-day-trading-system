# scalable-day-trading-system

### Initial architecture / tech stack

### Running with Docker

#### Backend

To start up the docker containers from the root directory type `docker compose up --build -d` and it will
build and run all the micro-services.

#### Frontend

To start up the webserver locally:

1. Install packages `npm i`
2. Start server `npm start`

### API Documentation

1. [Transaction Service](http://localhost:3001/transaction/docs)
2. [Authentication Service](http://localhost:3001/authentication/docs)
3. [Matching Engine Service](http://localhost:3001/engine/docs)
4. [Setup Service](http://localhost:3001/setup/docs)
