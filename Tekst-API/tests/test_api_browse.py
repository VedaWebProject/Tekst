import pytest

from httpx import AsyncClient
from tekst.models.resource import ResourceBaseDocument
from tekst.models.text import TextDocument


@pytest.mark.anyio
async def test_get_unit_siblings(
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    register_test_user,
    get_session_cookie,
):
    await insert_sample_data("texts", "nodes", "resources", "units")
    text = await TextDocument.find_one(TextDocument.slug == "pond")
    assert text
    resource = await ResourceBaseDocument.find_one(
        ResourceBaseDocument.text_id == text.id, with_children=True
    )
    assert resource

    resp = await test_client.get(
        "/browse/unit-siblings",
        params={"resourceId": str(resource.id)},
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 3
