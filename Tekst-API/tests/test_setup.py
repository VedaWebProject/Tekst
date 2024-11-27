import pytest

from tekst.setup import app_setup


@pytest.mark.anyio
async def test_setup():
    await app_setup()
    await app_setup()  # 2nd time to test setup attempt on already set-up instance
