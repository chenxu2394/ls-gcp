# Start from a fresh Python image
FROM python:3.8-slim

# Install necessary packages for building C++ code
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    cmake \
    net-tools \
    iproute2 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Flask, Gunicorn, and Google Cloud Storage client library
RUN pip install flask gunicorn google-cloud-storage

# Build the project
RUN git clone --recursive https://github.com/latticesurgery-com/liblsqecc.git && \
    cd liblsqecc && \
    mkdir build && cd build && \
    cmake .. && make
COPY server.py utils.py /liblsqecc/build/
# Expose port 8080
EXPOSE 8080

# Set the working directory to where the executable and server script are
WORKDIR /liblsqecc/build

# Set default environment variables
ENV USE_GCS=False
ENV NO_SLICES=False

# Start Gunicorn server with increased timeout and log settings
CMD ["gunicorn", \
     "--chdir", "/liblsqecc/build", \
     "--bind", "0.0.0.0:8080", \
     "--workers", "1", \
     "--timeout", "300", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "server:app"]
