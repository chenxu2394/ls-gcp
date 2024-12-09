# Start from a fresh Python image
FROM python:3.8-slim

# Install necessary packages for building C++ code
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Install Flask and Gunicorn
RUN pip install flask gunicorn

# Install Google Cloud Storage client library
RUN pip install google-cloud-storage

# Clone the liblsqecc repository
RUN git clone --recursive https://github.com/latticesurgery-com/liblsqecc.git

# Build the project
WORKDIR /liblsqecc
RUN mkdir build && cd build && cmake .. && make

# Copy the Python server script into the container
COPY server.py /liblsqecc/build/server.py
COPY utils.py /liblsqecc/build/utils.py

# Expose port 8080
EXPOSE 8080

# Set the working directory to where the executable and server script are
WORKDIR /liblsqecc/build

# Set default environment variables
ENV USE_GCS=False
ENV NO_SLICES=False

# Start Gunicorn server with increased timeout and log settings
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--timeout", "300", "--access-logfile", "-", "--error-logfile", "-", "server:app"]

