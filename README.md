# Vigilant

## Authenticate with user credentials

```shell
gcloud auth application-default login \
    --scopes=https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/spreadsheets,https://www.googleapis.com/auth/drive
```

## Required environment variables

- PORTAL_USERNAME
- PORTAL_PASSWORD
- PORTAL_LOGIN_URL
- PORTAL_HOME_URL
- CREDIT_TRANSACTIONS_URL

## Run application

```shell
poetry run vigilant
```

## Start service locally

```shell
poetry run uvicorn vigilant.app:app --host 0.0.0.0 --port 8080 --reload
```

## Start service in container with local changes

```shell
docker build -t vigilant .

docker run --rm \
    --cpus 1 --memory 1024M -p 8080:8080 \
    -v ./vigilant:/vigilant \
    -e PORTAL_USERNAME=$PORTAL_USERNAME \
    -e PORTAL_PASSWORD=$PORTAL_PASSWORD \
    -e PORTAL_LOGIN_URL=$PORTAL_LOGIN_URL \
    -e PORTAL_HOME_URL=$PORTAL_HOME_URL \
    -e CREDIT_TRANSACTIONS_URL=$CREDIT_TRANSACTIONS_URL \
    vigilant
```
