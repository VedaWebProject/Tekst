import pytest

from tekst.setup import app_setup


@pytest.mark.anyio
async def test_setup(use_indices):
    await app_setup()


@pytest.mark.anyio
async def test_setup_db_has_data(insert_sample_data):
    await insert_sample_data("texts", "locations", "resources")
    await app_setup()
