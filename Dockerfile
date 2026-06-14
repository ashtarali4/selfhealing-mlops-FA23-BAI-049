FROM python:3.10-slim

# Install Chrome dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    ca-certificates \
    --no-install-recommends

# Install Google Chrome (new method without apt-key)
RUN wget -q -O /usr/share/keyrings/google-chrome.gpg \
    https://dl.google.com/linux/linux_signing_key.pub \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] \
    http://dl.google.com/linux/chrome/deb/ stable main" \
    > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable --no-install-recommends

# Install webdriver-manager
RUN pip install --no-cache-dir webdriver-manager

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/logs

EXPOSE 5000

CMD ["python", "app.py"]
