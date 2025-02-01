### Authorization Service

This microservice handles authentication of users, creating accounts and issuing tokens to users

### Building And Running

**Make sure you have started the database microservice first, go to the database folder and see the readme for instructions to run that microservice.**

To run the app go to the **scalable-day-trading-system** directory (see notes below) and type `docker build -t auth -f authorization/Dockerfile .` then to run the app 
`docker run --rm --name auth -p 8000:8000 auth`. The `--rm --name auth` will delete the container each time so that you don't
end up with numerous containers. You can also open docker desktop and run it from in there if you prefer using the GUI, just enter the host port number.
**NOTE: if localhost:8000/docs or 0.0.0.0:8000/docs doesn't work, try 127.0.0.1:8000/docs** I found that on Debian I could use any of them, but on Windows 
0.0.0.0 didn't work, but localhost and 127.0.0.1 did. 

You need to be in the parent directory because it needs to have the correct build context as it uses files from the database microservice.
Make sure that the database microservice is running first. See the readme in the database folder for instructions to run it.
