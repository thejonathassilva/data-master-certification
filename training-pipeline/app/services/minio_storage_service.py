import io
import tarfile
import os
from typing import Any, Literal
import pickle
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


    def save_object(self, subject: str, component: Component, obj: Any) -> str:
        payload = pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)
        return self.save_bytes(subject, component, payload)

    def save_bytes(self, subject: str, component: Component, data: bytes) -> str:
        exists = self.exists(subject, component)
        if(exists):
            self.delete(subject, component)
            
        path = self._pkl_path(subject, component)
        stream = io.BytesIO(data)
        stream.seek(0)
        self.client.put_object(
            bucket_name=self.bucket,
            object_name=path,
            data=stream,
            length=len(data),
            content_type="application/octet-stream",
        )

        self.client.stat_object(self.bucket, path)
        return self._s3_uri(path)

    def exists(self, subject: str, component: Component) -> bool:
        path = self._pkl_path(subject, component)
        try:
            self.client.stat_object(self.bucket, path)
            return True
        except Exception:
            return False

    def delete(self, subject: str, component: Component) -> None:
        path = self._pkl_path(subject, component)
        self.client.remove_object(self.bucket, path)
