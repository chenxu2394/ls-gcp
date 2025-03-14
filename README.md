# Lattice Surgery Service Pipeline - Run Locally or on Google Cloud Run

## Overview

This repository provides a service pipeline for the [LibLSQECC](https://github.com/latticesurgery-com/liblsqecc) project, which is a high-performance compiler for generating lattice surgery instructions used in quantum computing. The service allows users to submit input files containing lattice surgery instructions and layout specifications via HTTP `POST` requests. It processes these inputs using the `lsqecc_slicer` executable and returns the output.

The service can be run locally using Docker or deployed to Google Cloud Run for scalable, serverless execution. When deployed on Google Cloud Run, it integrates with Google Cloud Storage to store and retrieve output files.

## Running Locally

### Prerequisites

Docker installed on the local machine.

### Steps

#### 1. Build the Docker Image

```bash
docker build -t ls_gunicorn_local .
```

#### 2. Run the Docker Image

```bash
docker run -p 8080:8080 -e USE_GCS=False -e NO_SLICES=True ls_gunicorn_local
```

#### 3. Test the Service

```bash
curl -X POST \
  -F "instructions=@$(pwd)/instructions.txt" \
  -F "layout=@$(pwd)/layout.txt" \
  localhost:8080/process
```

The response will be in the form of a JSON object.

## Running on Google Cloud Run

### 1. Creat a Google Cloud Storage Bucket

```bash
gsutil mb gs://[bucket_name]
```

### 2. Build the docker image using linux/amd64 and push it to the google artifact registry

```bash
docker buildx build --platform linux/amd64 -t gcr.io/[project_id]/ls_gunicorn --push .
```

### 3. Deploy the image to google cloud run

```bash
gcloud run deploy ls-gunicorn \
  --image gcr.io/[project_id]/ls_gunicorn \
  --platform managed \
  --region us-central1 \
  --set-env-vars USE_GCS=True,BUCKET_NAME=[bucket_name]
```

### 4. Set Up Permissions

Get the service account email

```bash
SERVICE_ACCOUNT_EMAIL=$(gcloud run services describe ls-gunicorn \
  --platform managed \
  --region us-central1 \
  --format 'value(spec.template.spec.serviceAccountName)')
```

Grant the Storage Object Creator role

```bash
gsutil iam ch serviceAccount:${SERVICE_ACCOUNT_EMAIL}:roles/storage.objectCreator gs://[bucket_name]
```

## 5. Test the service

Get the URL of the service

```bash
URL=$(gcloud run services describe ls-gunicorn \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)')
```

Get the token to authenticate the service

```bash
TOKEN=$(gcloud auth print-identity-token)
```

Send a POST request to the service

```bash
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -F "instructions=@$(pwd)/instructions.txt" \
  -F "layout=@$(pwd)/layout.txt" \
  ${URL}/process
```

The response will contain the `gs://` URL of the output file, which will be saved to the bucket with the name `instructions_layout.json`

## Run Stress Test using Vegeta

```bash
% echo "POST $URL/process" | vegeta attack -duration=100s -rate=1000 \
  -body=body.txt \
  -header "Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW" \
  -header "Authorization: Bearer $TOKEN" | vegeta report
Requests      [total, rate, throughput]         100000, 1000.01, 998.31
Duration      [total, attack, wait]             1m40s, 1m40s, 170.153ms
Latencies     [min, mean, 50, 90, 95, 99, max]  143.819ms, 162.251ms, 159.191ms, 170.287ms, 177.3ms, 211.162ms, 1.647s
Bytes In      [total, mean]                     2200000, 22.00
Bytes Out     [total, mean]                     48700000, 487.00
Success       [ratio]                           100.00%
Status Codes  [code:count]                      200:100000
Error Set:
```

## Run on Ubuntu with apptainer

### 1. Build the docker image using linux/amd64

```bash
docker build -t ls-gcp .
```

### 2. Build an apptainer sif file

```bash
apptainer build ls-gcp.sif docker-daemon://ls-gcp:latest
```

### 3. Run the apptainer sif file

```bash
apptainer run --writable-tmpfs --env NO_SLICES=True ls-gcp.sif
```

### 4. Test the service

Because apptainer share the same network with the host machine, we can send the request to the service using the host machine

```bash
curl -X POST -F "instructions=@$(pwd)/ZXCNOTDemo.qasm" -F "layout=@$(pwd)/layout.txt" http://localhost:8080/process
curl -X POST -F "instructions=@$(pwd)/instructions.txt" -F "layout=@$(pwd)/layout.txt" http://localhost:8080/process
```
