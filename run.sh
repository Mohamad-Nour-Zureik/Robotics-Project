#!/bin/bash

if [ -d "/usr/local/webots" ]; then
    export WEBOTS_HOME="/usr/local/webots"
elif [ -d "/snap/webots/current/usr/share/webots" ]; then
    export WEBOTS_HOME="/snap/webots/current/usr/share/webots"
else
    export WEBOTS_HOME="/usr/share/webots"
fi

export LD_LIBRARY_PATH="$WEBOTS_HOME/lib/controller:$LD_LIBRARY_PATH"
export PYTHONPATH="$WEBOTS_HOME/lib/controller/python:$PYTHONPATH"
export PYTHONPATH="$(pwd)/controllers:$PYTHONPATH"

launch_robot() {
    ROBOT_NAME="$1"
    SCRIPT_PATH="$2"
    
    echo "Launching $ROBOT_NAME via TCP..."
    
    export WEBOTS_CONTROLLER_URL="tcp://127.0.0.1:1234/$ROBOT_NAME"
    
    unset WEBOTS_ROBOT_NAME
    
    /usr/bin/python3 -u "$SCRIPT_PATH" &
}

echo "Connecting to Webots on localhost:1234..."

launch_robot "taker" "controllers/taker/taker.py"
launch_robot "correcter" "controllers/correcter/correcter.py"

echo "⏳ Controllers running. Press Ctrl+C to exit."
wait