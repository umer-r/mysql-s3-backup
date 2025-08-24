"""
    Keep only N newest local backups and optionally cleanup S3 using s3_client helpers.
"""

from pathlib import Path
from typing import List

from config import Config
from utils import get_logger
from s3_client import list_objects, delete_objects

logger = get_logger(__name__)


def cleanup_local(backups_dir: Path, keep: int):
    files = [p for p in backups_dir.iterdir() if p.is_file()]
    # sort by modification time descending
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    to_delete = files[keep:]
    for f in to_delete:
        try:
            f.unlink()
            logger.info("Deleted local backup: %s", f)
        except Exception as e:
            logger.exception("Failed to delete local backup %s: %s", f, e)


def cleanup_s3(cfg: Config, prefix: str, keep: int):
    # list objects under prefix and sort by LastModified desc
    objs = list_objects(cfg, prefix)
    objs.sort(key=lambda o: o["LastModified"], reverse=True)
    to_delete = objs[keep:]
    keys = [o["Key"] for o in to_delete]
    if keys:
        delete_objects(cfg, keys)