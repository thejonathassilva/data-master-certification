import io
import tarfile
import os
from typing import Any, Literal, Tuple
import pickle
from urllib.parse import urlparse
from app.adapters.minio_client import get_minio
from app.config import settings

Component = Literal["vectorizer", "classifier"]

class MinioStorageService:
    def __init__(self):
        self.client = get_minio()
        self.bucket = settings.minio_bucket
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)


    @staticmethod
    def _pkl_path(subject: str, component: Component) -> str:
        return f"{subject}/{component}.pkl"

    def _s3_uri(self, path_in_bucket: str) -> str:
        return f"s3://{self.bucket}/{path_in_bucket}"
    
    @staticmethod
    def _parse_s3_uri(s3_uri: str) -> Tuple[str, str]:
        if s3_uri.startswith("s3://"):
            p = urlparse(s3_uri)
            bucket = p.netloc
            object_name = p.path[1:] if p.path.startswith("/") else p.path
            return bucket, object_name
        return "", s3_uri


    def load_object(self, subject: str, component: Component) -> Any:

        data = self.load_bytes(subject, component)
        return pickle.loads(data)
    
    def load_from_minio_url(self, minio_url: str) -> Any:
        bucket, object_name = self._parse_s3_uri(minio_url)
        if not bucket:
            bucket = self.bucket
        resp = None
        try:
            resp = self.client.get_object(bucket, object_name)
            data = resp.read()
            return pickle.loads(data)
        finally:
            if resp is not None:
                try:
                    resp.close()
                finally:
                    if hasattr(resp, "release_conn"):
                        resp.release_conn()
