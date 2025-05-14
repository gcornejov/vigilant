FROM thehale/python-poetry:2.1.3-py3.12-slim AS build-deps

RUN poetry self add poetry-plugin-export

ADD . vigilant
WORKDIR /vigilant
RUN poetry export -o /requirements.txt --without-hashes --without-urls


FROM python:3.12-slim AS build-service

ARG CHROMEDRIVER_VERSION=136.0.7103.92

RUN apt update && apt upgrade
RUN DEBIAN_FRONTEND=noninteractive apt install -y wget unzip fonts-liberation libnspr4 libnss3 xdg-utils \
    libasound2 libatk-bridge2.0-0 libatk1.0-0 libatspi2.0-0 libcairo2 libcups2 libcurl3-gnutls libcurl3-nss \
    libcurl4 libgtk-3-0 libgtk-4-1 libpango-1.0-0 libvulkan1 libxdamage1 libxkbcommon0

RUN wget -O google-chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -i google-chrome.deb && \
    rm google-chrome.deb

RUN wget -O chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip && \
    unzip chromedriver.zip -d chromedriver && \
    cp chromedriver/chromedriver-linux64/chromedriver /usr/local/bin/ && \
    rm -r chromedriver chromedriver.zip

RUN mkdir -p -m 511 /usr/var/vigilant

COPY --from=build-deps /requirements.txt .
RUN pip install -r requirements.txt

ADD vigilant /vigilant

CMD ["uvicorn", "vigilant.app:app", "--host", "0.0.0.0", "--port", "8080"]
