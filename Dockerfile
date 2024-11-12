# Start from a fresh Python image
FROM python:3.8-slim

# Install necessary packages for building C++ code
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Install Flask and Gunicorn to serve HTTP requests
RUN pip install flask gunicorn

# Clone the liblsqecc repository
RUN git clone --recursive https://github.com/latticesurgery-com/liblsqecc.git

# Build the project
WORKDIR /liblsqecc
RUN mkdir build && cd build && cmake .. && make

# Copy the Python server script into the container
COPY server.py /liblsqecc/build/server.py

# Expose port 8080
EXPOSE 8080

# Set the working directory to where the executable and server script are
WORKDIR /liblsqecc/build

# Start Gunicorn server
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "server:app"]
