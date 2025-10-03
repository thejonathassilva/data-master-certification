from app.services.minio_storage_service import MinioStorageService

def test_minio_paths():
    assert MinioStorageService.subject_path("PF","CARTAO","v1") == "PF/CARTAO/v1/model.tar.gz"
    assert MinioStorageService.channel_path("PF","v2") == "PF/_channel/v2/model.tar.gz"
