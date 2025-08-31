# MySQL / MariaDB — Logical Backups → S3 (R2 / AWS)

A lightweight utility to create logical backups (using mysqldump / mariadb-dump) and optionally upload them to S3-compatible object storage (AWS S3, Cloudflare R2, etc.). Designed to run in Docker, cron jobs, or Kubernetes CronJobs.

## Features

- Create logical backups of one or multiple databases.
- Optional upload to S3-compatible object storage (supports custom endpoints for R2 and similar).
- Retention policy: keep a configurable number of backups (locally).

## Environment variables

Use environment variables to configure backup behavior. Reasonable defaults are provided where applicable.

| Variable | Description | Default / Required |
|---|---:|---|
| `DATABASE_CLIENT` | Tool used for dump (`mariadb` or `mysql`) | `mariadb` |
| `DATABASE_NAMES` | Comma-separated list of databases to dump. If empty, all databases are dumped into a single file. | (empty) |
| `DATABASE_USER` | MySQL user used for dumping | `root` |
| `DATABASE_USER_PASS` | Password for the DB user | **required** (or set via secret) |
| `DATABASE_HOST` | MySQL host | `localhost` |
| `DATABASE_PORT` | MySQL port | `3306` |
| `BACKUPS_TO_KEEP` | Number of backups to retain (local) | `7` |
| `S3_ENABLED` | Enable upload to S3-compatible storage (`True` / `False`) | `False` |
| `S3_BUCKET` | S3 bucket name (required if `S3_ENABLED=true`) | — |
| `S3_BUCKET_PREFIX` | Optional prefix/path inside the bucket | - |
| `S3_REGION` | S3 region (optional) | — |
| `S3_ENDPOINT_URL` | Custom S3 endpoint (for R2 / AWS / Other) | — |
| `S3_ACCESS_KEY` / `S3_SECRET_KEY` | Credentials for S3-compatible storage | — |
| `MYSQLDUMP_SSL_CA` | Path to CA file to enable TLS for dump connection | — |
| `MYSQLDUMP_SKIP_SSL` | Disable TLS for dump connection (**insecure**) | `False` |

## Notes & troubleshooting

- Shell quoting: when passing `DATABASE_USER_PASS` into a container or a Kubernetes secret, avoid adding extra quotes that become part of the value. For example:

```bash
# wrong — value will include the quotes
DATABASE_USER_PASS="secretpass"

# correct
DATABASE_USER_PASS=secretpass
```

- If you encounter authentication or access-denied errors, verify that the user, host, and privileges are configured correctly (see **User privileges** below).

## Build (Docker)

```bash
# Build image (from project root)
docker build -t mysql-s3-backup:latest .
```

## Run (example)

```bash
docker run --rm   -e DATABASE_USER=root   -e DATABASE_USER_PASS=secret   -e DATABASE_HOST=db-host.example.com   -e BACKUPS_TO_KEEP=14   -e S3_ENABLED=true   -e S3_BUCKET=my-backups-bucket   -e S3_ACCESS_KEY=AKIA...   -e S3_SECRET_KEY=...   mysql-s3-backup:latest
```

## Recommended database user privileges

For safety, do **not** use `root` in production. Create a dedicated backup user with the minimal required privileges:

```sql
CREATE USER 'backupuser'@'%' IDENTIFIED BY 'strong_password';
GRANT SELECT, SHOW VIEW, EVENT, TRIGGER, LOCK TABLES, RELOAD, PROCESS ON *.* TO 'backupuser'@'%';
FLUSH PRIVILEGES;
```

### Test dumping privileges

Run a manual dump to verify the backup user has the required access:

```bash
mysqldump -ubackupuser -p -h mysql_host -P3306   --single-transaction --skip-lock-tables --quick   --routines --events --triggers --databases db1 db2 > dump.sql
```

## Scheduling the backup

### Cron (host)

Example cron entry (daily at 02:00):

```cron
0 2 * * * docker run --rm -e DATABASE_USER=... -e DATABASE_USER_PASS=... -e DATABASE_HOST=... -e S3_ENABLED=true -e S3_BUCKET=... carb0n2019/mysql-s3-backup:0.1.1
```

### Kubernetes Cronjob

Read on my blog to deploy as [Kubernetes Cronjob](https://umerops.com/blog/scheduling-mysql-backups-using-kubernetes-cronjob-and-python).

## Security considerations

- Store credentials in secrets (Kubernetes secrets, Docker secrets, or environment management tools), avoid committing secrets to version control.
- `MYSQLDUMP_SKIP_SSL` disables TLS and is considered insecure. Only use it in isolated, trusted networks.

## Troubleshooting

- `access denied` errors: confirm the user/host combination and privileges. Check that the `DATABASE_HOST` is reachable from the container or pod.
- `connection refused`: verify `DATABASE_HOST` and `DATABASE_PORT`, and ensure the database allows connections from the source IP.
- S3 upload fails: confirm `S3_ENABLED=true`, correct bucket name, and valid `S3_ACCESS_KEY`/`S3_SECRET_KEY`. For custom endpoints, ensure `S3_ENDPOINT_URL` includes the correct scheme (`https://`).