import pytest

from tekst.setup import app_setup


@pytest.mark.anyio
async def test_setup(config):
    await app_setup(config)
