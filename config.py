"""
    Configuration parsing from environment variables.
"""

from dataclasses import dataclass
import os
from typing import List, Optional
from dotenv import load_dotenv 


load_dotenv()


def _env_bool(name: str, default: bool) -> bool:
    """
        Converts environment variable values to boolean. 
        Returns True for values like "1", "true", "yes", "y", "on" 
        (case-insensitive), otherwise returns the default.
    """
    v = os.getenv(name)
    if v is None:
        return default
    return v.lower() in ("1", "true", "yes", "y", "on")


def _env_int(name: str, default: int) -> int:
    """
        Converts an environment variable to an integer. 
        Returns the default if the variable is missing or not a valid integer.
    """
    v = os.getenv(name)
    try:
        return int(v) if v is not None else default
    except ValueError:
        return default


def _csv_to_list(s: Optional[str]) -> List[str]:
    """
        Splits a comma-separated string (e.g., "db1, db2") into a list of trimmed strings. 
        Returns an empty list if input is empty.
    """
    if not s:
        return []
    return [x.strip() for x in s.split(",") if x.strip()]


@dataclass
class Config:
    database_names: List[str]
    backups_to_keep: int
    database_user: str
    database_user_pass: str
    database_host: str
    database_port: int
    database_client: Optional[str]

    s3_enabled: bool
    s3_bucket: Optional[str]
    s3_prefix: Optional[str]
    s3_region: Optional[str]
    s3_endpoint_url: Optional[str]
    s3_access_key: Optional[str]
    s3_secret_key: Optional[str]
    
    mysqldump_skip_ssl: Optional[bool]
    mysqldump_ssl_ca: Optional[str]


def load_config() -> Config:
    database_names = _csv_to_list(os.getenv("DATABASE_NAMES"))
    backups_to_keep = _env_int("BACKUPS_TO_KEEP", 7)
    database_user = os.getenv("DATABASE_USER", "root")
    database_user_pass = os.getenv("DATABASE_USER_PASS", "")
    database_host = os.getenv("DATABASE_HOST", "localhost")
    database_port = _env_int("DATABASE_PORT", 3306)
    database_client = os.getenv("DATABASE_CLIENT", "mariadb")

    s3_enabled = _env_bool("S3_ENABLED", False)
    s3_bucket = os.getenv("S3_BUCKET")
    s3_region = os.getenv("S3_REGION")
    s3_endpoint_url = os.getenv("S3_ENDPOINT_URL")
    s3_access_key = os.getenv("S3_ACCESS_KEY")
    s3_secret_key = os.getenv("S3_SECRET_KEY")
    s3_prefix = os.getenv("S3_BUCKET_PREFIX")
    
    mysqldump_skip_ssl = _env_bool("MYSQLDUMP_SKIP_SSL", False)
    mysqldump_ssl_ca = os.getenv("MYSQLDUMP_SSL_CA")

    return Config(
        database_names=database_names,
        backups_to_keep=backups_to_keep,
        database_user=database_user,
        database_user_pass=database_user_pass,
        database_host=database_host,
        database_port=database_port,
        database_client=database_client,
        s3_enabled=s3_enabled,
        s3_bucket=s3_bucket,
        s3_region=s3_region,
        s3_endpoint_url=s3_endpoint_url,
        s3_access_key=s3_access_key,
        s3_secret_key=s3_secret_key,
        s3_prefix=s3_prefix,
        mysqldump_skip_ssl=mysqldump_skip_ssl,
        mysqldump_ssl_ca=mysqldump_ssl_ca        
    )