### Database Service
This microservice is for the PostgreSQL database

**Make sure you run this before you run other API services such as Authorization service. It should be up and running so that the other services are able to connect to the postgres database**

### Building and Running
From the database directory run `docker-compose up --build` and the service should build and start running. If you want
to connect a local terminal to the database service you can type `psql -h localhost -p 5433 -U admin -d day_trader` then
enter the password (in the .env file). You can manually edit the database.

