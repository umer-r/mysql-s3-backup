# MySQL Logical Backup → S3 (R2/AWS)

## Environment variables

- `DATABASE_NAMES` — comma-separated DB names to dump. If empty or unset, the script will dump all databases into a single logical backup file.
- `DATABASE_USER` — MySQL user for dumping (default: `root`).
- `DATABASE_USER_PASS` — password for the MYSQL Database user.
- `DATABASE_HOST` — MySQL host (default: `localhost`).
- `DATABASE_PORT` — MySQL port (default: `3306`).
- `BACKUPS_TO_KEEP` — integer number of backups to keep (default: `7`).
- `S3_ENABLED` — `true` or `false` (default: `false`).
- `S3_BUCKET` — bucket name to upload to (required if `S3_ENABLED=true`).
- `S3_BUCKET_PREFIX` — optional prefix used inside the bucket (default: `backups/`).
- `S3_REGION` — optional region.
- `S3_ENDPOINT_URL` — optional endpoint (for R2 or other S3-compatible providers).
- `S3_ACCESS_KEY` / `S3_SECRET_KEY` — credentials for S3-compatible storage.
- `MYSQLDUMP_SKIP_SSL` — **Insecure** Disable TLS mode.

## Notes
> **1:** If getting an Issue with user access denied try removing the qoutes from the user pass
>
> **E.g:** 
> 
>   `DATABASE_USER_PASS="secretpass"` <-- Error
> 
>   `DATABASE_USER_PASS=secretpass` <-- Correct

## Build and run (Docker)

```bash
# build
docker build -t mysql-backup:latest .

# run (example)
docker run --rm \
  -e DATABASE_USER=root \
  -e DATABASE_USER_PASS=secret \
  -e DATABASE_HOST=db-host.example.com \
  -e BACKUPS_TO_KEEP=14 \
  -e S3_ENABLED=true \
  -e S3_BUCKET=my-backups-bucket \
  -e S3_ACCESS_KEY=AKIA... \
  -e S3_SECRET_KEY=... \
  mysql-backup:latest
```

## Use a cron

```bash
0 2 * * * docker run --rm \
  -e DATABASE_USER=... \
  ... \
  mysql-backup:latest
```