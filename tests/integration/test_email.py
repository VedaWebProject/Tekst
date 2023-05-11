import pytest

from tekst.email import send_test_email
from tekst.models.user import UserRead


@pytest.mark.anyio
async def test_sending_email():
    send_test_email(
        UserRead(
            id="645b469846c001259ec09d63",
            username="testuser",
            email="testuser@test.com",
            first_name="Foo",
            last_name="Bar",
            affiliation="Baz",
            is_active=True,
            is_verified=True,
            is_superuser=False,
        )
    )
