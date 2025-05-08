from datetime import UTC, datetime

import pytest

from tekst.models.user import UserRead
from tekst.notifications import send_test_email


@pytest.mark.anyio
async def test_sending_email():
    await send_test_email(
        UserRead(
            id="645b469846c001259ec09d63",
            username="testuser",
            email="testuser@tekst.dev",
            name="Foo Bar",
            affiliation="Baz",
            is_active=True,
            is_verified=True,
            is_superuser=False,
            created_at=datetime.now(UTC),
        )
    )
