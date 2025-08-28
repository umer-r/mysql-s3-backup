"""
    Create logical mysql dump using mysqldump and compress to gzip while streaming.
"""

import subprocess
import gzip
import shutil
from datetime import datetime
from pathlib import Path

from config import Config
from utils import get_logger

logger = get_logger(__name__)


def _build_mysqldump_command(cfg: Config) -> list:
    base = [
        "mysqldump",
        f"-u{cfg.database_user}",
        f"-h{cfg.database_host}",
        f"-P{cfg.database_port}",
        # recommended options for consistent dumps
        "--single-transaction",
        "--skip-lock-tables",
        "--quick",
        "--routines",
        "--events",
        "--triggers",
    ]
    
    if cfg.mysqldump_skip_ssl:
        if cfg.database_client == "mariadb":
            base.append("--skip-ssl")
        else:
            base.append("--ssl-mode=DISABLED")
        
    if cfg.mysqldump_ssl_ca:
        if cfg.database_client == "mariadb":
            base.append(f"--ssl-ca={cfg.mysqldump_ssl_ca}")
            base.append("--ssl-verify-server-cert=0")
        else:
            base.append(f"--ssl-ca={cfg.mysqldump_ssl_ca}")
            base.append("--ssl-mode=REQUIRED")

    if not cfg.database_names:
        base.append("--all-databases")
    else:
        base.append("--databases")
        base.extend(cfg.database_names)

    return base


def create_dump(cfg: Config, out_dir: Path) -> Path:
    """
        Runs mysqldump and writes a gzipped file into out_dir.
        Returns path to the created file.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    
    if not cfg.database_names:
        name_part = "all-databases"
    else:
        name_part = "-".join(x.replace("/", "_") for x in cfg.database_names)

    filename = f"mysql-backup-{name_part}-{ts}.sql.gz"
    out_path = out_dir / filename

    cmd = _build_mysqldump_command(cfg)
    # Remove all (") qoutations from the cmd
    cmd = [arg.replace('"', '').replace("'", '') for arg in cmd]
    logger.info("Running mysqldump: %s", " ".join(cmd))

    env = None
    # use MYSQL_PWD to avoid password on cmdline
    if cfg.database_user_pass:
        env = {**subprocess.os.environ, "MYSQL_PWD": cfg.database_user_pass}

    # Stream mysqldump stdout to gzip file to avoid high memory usage
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env) as proc:
        if proc.stdout is None:
            raise RuntimeError("mysqldump did not produce stdout")
        with gzip.open(out_path, "wb") as gz:
            try:
                shutil.copyfileobj(proc.stdout, gz)
            except Exception:
                proc.kill()
                raise
        rc = proc.wait()
        if rc != 0:
            stderr = proc.stderr.read().decode(errors="ignore") if proc.stderr else ""
            logger.error("mysqldump failed (rc=%s): %s", rc, stderr)
            raise RuntimeError(f"mysqldump failed (rc={rc}): {stderr}")

    logger.info("Created backup: %s", out_path)
    return out_path