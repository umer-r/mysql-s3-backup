"""
    Keep only N newest local backups.
"""

from pathlib import Path
from utils import get_logger

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
