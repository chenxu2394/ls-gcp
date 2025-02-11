#!/bin/bash

# Function to cleanup processes on exit
cleanup() {
    # Kill the main apptainer process and its children
    if [ ! -z "$APPTAINER_PID" ]; then
        pkill -P "$APPTAINER_PID"
        kill -9 "$APPTAINER_PID" 2>/dev/null
    fi
    
    # Kill any remaining apptainer processes
    pkill -9 -f "apptainer run.*ls-gcp.sif"
    
    # Kill any process using port 8080
    sudo fuser -k 8080/tcp 2>/dev/null
    
    # Additional cleanup for gunicorn processes
    pkill -9 -f "gunicorn"
    
    # Wait briefly to ensure processes are terminated
    sleep 2
}

# Set trap to ensure cleanup runs on script exit
trap cleanup EXIT INT TERM

# Start the server instance in the background
nohup apptainer run --writable-tmpfs --env NO_SLICES=True ls-gcp.sif > /dev/null 2>&1 &

# Store the PID
APPTAINER_PID=$!

# Wait a few seconds for the server to initialize
sleep 5

# Run the Python script to generate layouts and send requests
python3 gen.py 5 5 1 2 2 instructions.txt

# Cleanup at the end
cleanup