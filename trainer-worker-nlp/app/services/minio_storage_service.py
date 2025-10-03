import io
import tarfile
import os
from typing import Optional
from app.adapters.minio_client import get_minio
from app.config import settings

class MinioStorageService:
    def __init__(self):
        self.client = get_minio()
        self.bucket = settings.minio_bucket
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    @staticmethod
    def subject_path(channel: str, subject_name: str, version: str) -> str:
        return f"{channel}/{subject_name}/{version}/model.tar.gz"

    @staticmethod
    def channel_path(channel: str, version: str) -> str:
        return f"{channel}/_channel/{version}/model.tar.gz"

    def upload_dir_as_tar_gz(self, path_in_bucket: str, local_dir: str) -> str:
        data = io.BytesIO()
        with tarfile.open(fileobj=data, mode="w:gz") as tar:
            tar.add(local_dir, arcname="model")
        data.seek(0)

        self.client.put_object(
            bucket_name=self.bucket,
            object_name=path_in_bucket,
            data=data,
            length=len(data.getbuffer()),
            content_type="application/gzip"
        )
        self.client.stat_object(self.bucket, path_in_bucket)

        return f"s3://{self.bucket}/{path_in_bucket}"

    def download_to_dir(self, path_in_bucket: str, dest_dir: str):
        obj = self.client.get_object(self.bucket, path_in_bucket)
        tgz = io.BytesIO(obj.read())
        obj.close()
        obj.release_conn()
        os.makedirs(dest_dir, exist_ok=True)
        with tarfile.open(fileobj=tgz, mode="r:gz") as tar:
            tar.extractall(dest_dir)

    def exists(self, path_in_bucket: str) -> bool:
        try:
            self.client.stat_object(self.bucket, path_in_bucket)
            return True
        except Exception:
            return False
