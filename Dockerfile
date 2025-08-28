FROM python:3.11-alpine

RUN adduser -D -h /home/backupuser backupuser \
 && mkdir -p /app/backups \
 && chown -R backupuser:backupuser /app

WORKDIR /app

# Alpine's "mysql-client" is MariaDB client
RUN apk add --no-cache \
    mysql-client \
    && rm -rf /var/cache/apk/*

COPY --chown=backupuser:backupuser requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY --chown=backupuser:backupuser . /app

USER backupuser

ENTRYPOINT ["python", "main.py"]
