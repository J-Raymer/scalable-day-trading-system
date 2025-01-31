### Authorization Service

This microservice handles authentication of users, creating accounts and issuing tokens to users

### Building And Running

To run the app go to the **parent** directory and type `docker build -t auth -f authorization/Dockerfile .` then to run the app 
`docker run --network="host" -p 8000:8000 auth`.

You need to be in the parent directory because it needs to have the correct build context as it uses files from the database microservice.
Make sure that the database microservice is running first. See the readme in the database folder for instructions to run it.
