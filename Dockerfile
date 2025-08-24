# Dockerfile — python slim image with mysql client installed
FROM python:3.11-slim

# install packages needed for mysqldump and for building dependencies
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
       default-mysql-client \
       ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# copy app
COPY . /app

# Create backups directory
RUN mkdir -p /app/backups

# use a non-root user if desired (optional)
# RUN useradd -m backupuser && chown -R backupuser /app
# USER backupuser

ENTRYPOINT ["python", "main.py"]