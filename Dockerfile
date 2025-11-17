FROM thehale/python-poetry:2.1.3-py3.12-slim AS build-deps

RUN poetry self add poetry-plugin-export

ADD . vigilant
WORKDIR /vigilant
RUN poetry export -o /requirements.txt --without-hashes --without-urls


FROM python:3.12-slim AS build-service

RUN apt update -y && apt upgrade -y

# Create app folder
RUN mkdir -p -m 777 /var/lib/vigilant

# Install dependencies
COPY --from=build-deps /requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Install Chrome Browser and Driver
RUN playwright install chrome --with-deps

# Copy app source code
ADD vigilant /vigilant

CMD ["uvicorn", "vigilant.app:app", "--host", "0.0.0.0", "--port", "8080"]
