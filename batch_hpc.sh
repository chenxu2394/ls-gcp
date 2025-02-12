#!/bin/bash

# Start the server instance in the background
nohup apptainer run --writable-tmpfs --env NO_SLICES=True ls-gcp.sif > /dev/null 2>&1 &

# Store the PID
APPTAINER_PID=$!

# Wait a few seconds for the server to initialize
sleep 5

# Run the Python script to generate layouts and send requests
python3 gen.py 5 5 1 2 2 instructions.txt