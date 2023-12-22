import pytest


@pytest.mark.anyio
async def test_openapi(test_app):
    assert "info" in test_app.openapi()
