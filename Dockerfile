# Start from a fresh Python image
FROM python:3.8-slim

# Install necessary packages for building C++ code
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Install Flask to serve HTTP requests
RUN pip install flask

# Clone the liblsqecc repository
RUN git clone --recursive https://github.com/latticesurgery-com/liblsqecc.git

# Build the project
WORKDIR /liblsqecc
RUN mkdir build && cd build && cmake .. && make

# Copy the Python server script into the container
COPY server.py /server.py

# Expose port 8080
EXPOSE 8080

# Set the working directory to where the executable is
WORKDIR /liblsqecc/build

# Start the HTTP server
CMD ["python", "/server.py"]
