FROM thehale/python-poetry:2.1.3-py3.12-slim AS build-deps

RUN poetry self add poetry-plugin-export

ADD . vigilant
WORKDIR /vigilant
RUN poetry export -o /requirements.txt --without-hashes --without-urls


FROM python:3.12-slim AS build-service

RUN apt update -y && apt upgrade -y
RUN apt install -y curl jq wget unzip

# Install Chrome Browser
RUN wget -O google-chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && dpkg -i google-chrome.deb || apt -f install -y

# Install Chrome Driver
RUN CHROME_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json" | jq '.channels.Stable.version' -r) \
    && wget -O chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/$CHROME_VERSION/linux64/chromedriver-linux64.zip \
    && unzip chromedriver.zip -d chromedriver \
    && cp chromedriver/chromedriver-linux64/chromedriver /usr/local/bin/

RUN rm -r google-chrome.deb chromedriver chromedriver.zip

# Create app folder
RUN mkdir -p -m 777 /var/lib/vigilant

# Install dependencies
COPY --from=build-deps /requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy app source code
ADD vigilant /vigilant

CMD ["uvicorn", "vigilant.app:app", "--host", "0.0.0.0", "--port", "8080"]
