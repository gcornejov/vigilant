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
