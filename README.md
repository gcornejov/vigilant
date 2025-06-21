# Vigilant

<p align="left">
    <a href="https://www.python.org/doc/versions/" target="_blank">
        <img alt="Python Version from PEP 621 TOML" src="https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fgcornejov%2Fvigilant%2Fmain%2Fpyproject.toml&logo=Python&labelColor=ffde57&color=4584b6" alt="Python version">
    </a>
    <a href="https://codecov.io/gh/gcornejov/vigilant">
        <img src="https://codecov.io/gh/gcornejov/vigilant/graph/badge.svg?token=VIWE3BIDB3" alt="Code coverage"/>
    </a>
</p>

## Authenticate with user credentials

```shell
gcloud auth application-default login \
    --billing-project ${GCP_PROJECT_ID} \
    --scopes https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/spreadsheets,https://www.googleapis.com/auth/drive
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
    -v /tmp:/tmp \
    -v ${HOME}/.config/gcloud:/root/.config/gcloud \
    -v ${LOCAL_WORKSPACE_FOLDER}/vigilant:/vigilant \
    -e PORTAL_USERNAME=$PORTAL_USERNAME \
    -e PORTAL_PASSWORD=$PORTAL_PASSWORD \
    -e PORTAL_LOGIN_URL=$PORTAL_LOGIN_URL \
    -e PORTAL_HOME_URL=$PORTAL_HOME_URL \
    -e CREDIT_TRANSACTIONS_URL=$CREDIT_TRANSACTIONS_URL \
    vigilant
```
