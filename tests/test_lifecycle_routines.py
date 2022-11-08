import pytest
from textrig.app import shutdown_routine, startup_routine


@pytest.mark.anyio
async def test_startup():
    await startup_routine()


@pytest.mark.anyio
async def test_shutdown():
    await shutdown_routine()
