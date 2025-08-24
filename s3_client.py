"""
    Simple S3 client helpers using boto3 that support custom endpoints (R2).
"""

import boto3
from botocore.client import Config as BotoConfig
from typing import Optional, List

from config import Config
from utils import get_logger

logger = get_logger(__name__)


def make_s3_client(cfg: Config):
    session = boto3.session.Session()
    client_kwargs = {}
    if cfg.s3_region:
        client_kwargs["region_name"] = cfg.s3_region

    if cfg.s3_endpoint_url:
        client_kwargs["endpoint_url"] = cfg.s3_endpoint_url
        # For many S3-compatible providers, signature version may need to be specified.
        botoconf = BotoConfig(signature_version="s3v4")
    else:
        botoconf = None

    if cfg.s3_access_key and cfg.s3_secret_key:
        client = session.client(
            "s3",
            aws_access_key_id=cfg.s3_access_key,
            aws_secret_access_key=cfg.s3_secret_key,
            config=botoconf,
            **client_kwargs,
        )
    else:
        client = session.client("s3", config=botoconf, **client_kwargs)

    return client


def upload_file(cfg: Config, filepath: str, key: str):
    client = make_s3_client(cfg)
    logger.info("Uploading %s to s3://%s/%s", filepath, cfg.s3_bucket, key)
    client.upload_file(Filename=filepath, Bucket=cfg.s3_bucket, Key=key)
    logger.info("Upload complete: %s", key)


def list_objects(cfg: Config, prefix: str) -> List[dict]:
    client = make_s3_client(cfg)
    paginator = client.get_paginator("list_objects_v2")
    objs = []
    for page in paginator.paginate(Bucket=cfg.s3_bucket, Prefix=prefix):
        for o in page.get("Contents", []):
            objs.append(o)
    return objs


def delete_objects(cfg: Config, keys: List[str]):
    if not keys:
        return
    client = make_s3_client(cfg)
    # batch delete (max 1000 per call)
    for i in range(0, len(keys), 1000):
        chunk = keys[i : i + 1000]
        delete_payload = {"Objects": [{"Key": k} for k in chunk]}
        resp = client.delete_objects(Bucket=cfg.s3_bucket, Delete=delete_payload)
        logger.info("Deleted objects: %s", chunk)