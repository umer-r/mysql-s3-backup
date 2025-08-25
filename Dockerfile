FROM python:3.11-alpine

# Install only the necessary MySQL client tools
RUN apk update && \
    apk add --no-cache \
    mysql-client \
    && rm -rf /var/cache/apk/*

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Create backups directory
RUN mkdir -p /app/backups

# Use a non-root user for security
RUN adduser -D backupuser && chown -R backupuser /app
USER backupuser

ENTRYPOINT ["python", "main.py"]