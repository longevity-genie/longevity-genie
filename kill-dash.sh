
#!/bin/bash

# Default port to 8050
PORT=${1:-8050}

# Get the PID of the process listening to the specified port
PID=$(lsof -t -i:$PORT)

# Kill the process if it exists
if [ ! -z "$PID" ]; then
    echo "Killing process with PID $PID that's listening on port $PORT"
    kill -9 $PID
else
    echo "No process found listening on port $PORT"
fi
