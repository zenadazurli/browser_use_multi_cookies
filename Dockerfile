FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

RUN pip install browser-use-sdk playwright supabase flask
RUN playwright install chromium
RUN playwright install-deps

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY config.py .
COPY app.py .

EXPOSE 10000

CMD ["python", "-u", "app.py"]
