# A pipeline to run the lattice surgery as a service on google cloud run

## Instructions

### 1. Build the docker image using linux/amd64 and push it to the google artifact registry

```bash
docker buildx build --platform linux/amd64 -t ls_gunicorn --load .
docker tag ls_gunicorn gcr.io/[project_id]/ls_gunicorn
docker push gcr.io/[project_id]/ls_gunicorn
```

### 2. Deploy the image to google cloud run

```bash
gcloud run deploy ls-image \
  --image gcr.io/[project_id]/ls_image:latest \
  --platform managed \
  --region us-central1
```

## 3. Get the URL of the deployed service

```bash
gcloud run services describe ls-gunicorn --platform managed --region us-central1 --format 'value(status.url)'
```

## 4. Get the token to authenticate the service

```bash
TOKEN=$(gcloud auth print-identity-token)
```

## 5. Test the service

```bash
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -F "instructions=@$(pwd)/instructions.txt" \
  -F "layout=@$(pwd)/layout.txt" \
  [url]/process
```
