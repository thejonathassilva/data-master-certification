from app.services.versioning_service import VersioningService

class FakeRepo:
    def __init__(self, versions):
        self.versions = versions
    def list_versions(self, scope, subject_id, channel):
        return self.versions

def test_auto_increments_last_version():
    repo = FakeRepo([{"version":"v1"}, {"version":"v3"}])
    svc = VersioningService(repo)
    v = svc.resolve_target_version("auto","subject","S1",None,None)
    assert v == "v4"

def test_fixed_uses_base_version():
    repo = FakeRepo([{"version":"v2"}])
    svc = VersioningService(repo)
    v = svc.resolve_target_version("fixed","subject","S1",None,"v10")
    assert v == "v10"
