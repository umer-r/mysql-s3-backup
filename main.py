"""
    Entrypoint: loads config, performs dump, optional upload and retention cleanup.
"""

from pathlib import Path
import sys
from config import load_config
from mysql_dump import create_dump
from retention import cleanup_local
from s3_client import upload_file
from utils import get_logger

logger = get_logger(__name__)


def main():
    cfg = load_config()
    backups_dir = Path("./backups")

    try:
        backup_path = create_dump(cfg, backups_dir)
    except Exception as e:
        logger.exception("Backup failed: %s", e)
        sys.exit(2)

    # upload to S3 if enabled
    if cfg.s3_enabled:
        if not cfg.s3_bucket:
            logger.error("S3 enabled but S3_BUCKET is not set")
        else:
            if cfg.s3_prefix and cfg.s3_prefix != "":
                key = f"{cfg.s3_prefix.rstrip('/')}/{backup_path.name}"
            else:
                key = backup_path.name
            
            try:
                upload_file(cfg, str(backup_path), key)
            except Exception:
                logger.exception("Upload failed")

    # cleanup local
    try:
        cleanup_local(backups_dir, cfg.backups_to_keep)
    except Exception:
        logger.exception("Local retention cleanup failed")


if __name__ == "__main__":
    main()