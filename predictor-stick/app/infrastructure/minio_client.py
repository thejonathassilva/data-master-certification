import os
import tarfile
import hashlib
import tempfile
from minio import Minio
from urllib.parse import urlparse
from app.core.config import settings

_minio = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_SECURE
)

def parse_minio_uri(uri: str):
    # Ex.: s3://nlp-models/PF/_channel/1.0.0/model.tar.gz
    parsed = urlparse(uri)
    if parsed.scheme != "s3":
        raise ValueError(f"Unsupported scheme: {parsed.scheme}")
    bucket = parsed.netloc or settings.MINIO_DEFAULT_BUCKET
    path = parsed.path.lstrip("/")
    return bucket, path

def ensure_bucket(bucket: str):
    if not _minio.bucket_exists(bucket):
        _minio.make_bucket(bucket)

def download_and_extract(uri: str, cache_dir: str) -> str:
    os.makedirs(cache_dir, exist_ok=True)
    bucket, path = parse_minio_uri(uri)
    # unique dir by sha1 of uri
    h = hashlib.sha1(uri.encode()).hexdigest()
    target_dir = os.path.join(cache_dir, h)
    if os.path.isdir(target_dir) and os.listdir(target_dir):
        return target_dir

    ensure_bucket(bucket)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".tar.gz") as tmpfile:
        _minio.fget_object(bucket, path, tmpfile.name)

    os.makedirs(target_dir, exist_ok=True)
    with tarfile.open(tmpfile.name, "r:gz") as tar:
        tar.extractall(target_dir)
    try:
        os.unlink(tmpfile.name)
    except Exception:
        pass
    return target_dir
