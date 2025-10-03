import pytest

@pytest.mark.asyncio
async def test_cache_bust_all(client):
    r = await client.post("/admin/cache/bust", json={})
    assert r.status_code == 200
    assert r.json()["cleared"] == "all"
