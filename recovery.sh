#!/bin/bash

# This script is used to start server program,
# and keep monitoring the server program and 
# automatically restart server if the program
# is killed.

PROGRAM_NAME="python server.py -s S1 -p 7777"

while true; do
    # check running status
    if pgrep -f "$PROGRAM_NAME" > /dev/null
    then
        # echo "running..."
        sleep 3
    else
        echo "start server..."
        sleep 10
        $PROGRAM_NAME
        exit_status=$?

        if [ $exit_status -ne 0 ]; then
            echo "restart..."
        fi
    fi
done

