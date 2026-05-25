#!/usr/bin/env python3
"""
Upload Coaching Phase Videos to S3.

One-time / occasional ops tooling, not a request-path utility. Reads the
local `videos/*.mov` files (which are gitignored — see `.gitignore:64-65`)
and uploads each one to BOTH the staging and production S3 buckets under
the `session-videos/` prefix so the feature works in every environment
after a single operator session.

Idempotent: by default, skips S3 keys that already exist. Pass `--force`
to re-upload regardless. Pass `--dry-run` to print intended actions
without touching S3.

The mapping between local filenames and S3 keys lives in
`server/apps/coach_states/constants/session_videos.py` — this script reads
the `s3_key` field from each registry entry, then derives the local
filename by stripping the `session-videos/` prefix and looking under
`videos/` at the repo root.

Required env vars:
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY  — must have write access
    AWS_REGION                                 — defaults to us-east-1

Usage:
    cd <repo root>
    AWS_ACCESS_KEY_ID=... AWS_SECRET_ACCESS_KEY=... \\
        python scripts/upload_session_videos.py
    python scripts/upload_session_videos.py --dry-run
    python scripts/upload_session_videos.py --force --bucket staging
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import sys
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

REPO_ROOT = Path(__file__).resolve().parent.parent
VIDEOS_DIR = REPO_ROOT / "videos"

# Load SESSION_VIDEOS directly from the source file rather than importing via
# `apps.coach_states.constants.session_videos` — the latter triggers
# `apps/__init__.py`, which imports celery_config, which touches Django
# settings. We don't want a Django bootstrap for an ops script. The registry
# module itself is pure Python at top level (`from django.conf import settings`
# is lazy — only `get_video_url` actually accesses settings, and this script
# doesn't call it).
_REGISTRY_PATH = (
    REPO_ROOT / "server" / "apps" / "coach_states" / "constants" / "session_videos.py"
)
_spec = importlib.util.spec_from_file_location("_session_videos", _REGISTRY_PATH)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
SESSION_VIDEOS = _mod.SESSION_VIDEOS

STAGING_BUCKET = "discovita-dev-coach-staging"
PRODUCTION_BUCKET = "discovita-dev-coach-production"
ALL_BUCKETS = (STAGING_BUCKET, PRODUCTION_BUCKET)


def s3_key_exists(s3, bucket: str, key: str) -> bool:
    try:
        s3.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError as err:
        if err.response["Error"]["Code"] in ("404", "NoSuchKey", "NotFound"):
            return False
        raise


def upload_one(
    s3,
    bucket: str,
    local_path: Path,
    s3_key: str,
    *,
    force: bool,
    dry_run: bool,
) -> str:
    """Upload one video to one bucket. Returns a status string."""
    if not local_path.exists():
        return f"MISSING local: {local_path}"

    if not force and s3_key_exists(s3, bucket, s3_key):
        return f"skip   (exists)  s3://{bucket}/{s3_key}"

    if dry_run:
        return f"DRY    would put  s3://{bucket}/{s3_key}  <- {local_path.name}"

    s3.upload_file(
        Filename=str(local_path),
        Bucket=bucket,
        Key=s3_key,
        ExtraArgs={
            "ContentType": "video/quicktime",
            "CacheControl": "public, max-age=31536000, immutable",
        },
    )
    return f"OK     uploaded   s3://{bucket}/{s3_key}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--bucket",
        choices=["both", "staging", "production"],
        default="both",
        help="Which bucket(s) to upload to (default: both).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-upload even if the key already exists on S3.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print intended actions without touching S3.",
    )
    args = parser.parse_args()

    buckets = ALL_BUCKETS
    if args.bucket == "staging":
        buckets = (STAGING_BUCKET,)
    elif args.bucket == "production":
        buckets = (PRODUCTION_BUCKET,)

    region = os.environ.get("AWS_REGION", "us-east-1")
    s3 = boto3.client(
        "s3",
        region_name=region,
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    )

    print(f"region={region}  buckets={list(buckets)}  "
          f"force={args.force}  dry_run={args.dry_run}")
    print(f"local source: {VIDEOS_DIR}")
    print()

    failures = 0
    for video_key, entry in SESSION_VIDEOS.items():
        s3_key = entry["s3_key"]
        local_filename = Path(s3_key).name
        local_path = VIDEOS_DIR / local_filename
        print(f"[{video_key}]  ({entry['name']})")
        for bucket in buckets:
            try:
                status = upload_one(
                    s3, bucket, local_path, s3_key,
                    force=args.force, dry_run=args.dry_run,
                )
                print(f"  {status}")
                if status.startswith(("MISSING", "ERROR")):
                    failures += 1
            except Exception as e:  # noqa: BLE001
                print(f"  ERROR  {bucket}: {e}")
                failures += 1
        print()

    print(f"Done. failures={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
