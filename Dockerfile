FROM python:3.11-alpine

# build-time args (defaults)
ARG VERSION="dev"
ARG VCS_REF="unknown"
ARG BUILD_DATE="unknown"

LABEL org.opencontainers.image.vendor="Umer Mehmood" \
      org.opencontainers.image.url="https://github.com/umer-r/mysql-s3-backup.git" \
      org.opencontainers.image.title="Mysql S3 Backup" \
      org.opencontainers.image.description="Logical Backups for Mysql/MariaDB and optionally push to S3 compatible storage." \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.documentation="https://github.com/umer-r/mysql-s3-backup/blob/master/README.md" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.created="${BUILD_DATE}"

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
