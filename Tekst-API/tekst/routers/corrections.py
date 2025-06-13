from datetime import UTC, datetime
from typing import Annotated

from beanie import PydanticObjectId
from fastapi import APIRouter, Path, status

from tekst import errors
from tekst.auth import UserDep
from tekst.i18n import pick_translation
from tekst.models.correction import CorrectionCreate, CorrectionDocument, CorrectionRead
from tekst.models.location import LocationDocument
from tekst.models.notifications import TemplateIdentifier
from tekst.models.resource import ResourceBaseDocument
from tekst.models.text import TextDocument
from tekst.models.user import UserDocument
from tekst.notifications import send_notification


router = APIRouter(
    prefix="/corrections",
    tags=["corrections"],
)


@router.post(
    "",
    response_model=CorrectionRead,
    status_code=status.HTTP_201_CREATED,
    responses=errors.responses(
        [
            errors.E_404_RESOURCE_NOT_FOUND,
            errors.E_404_CONTENT_NOT_FOUND,
            errors.E_400_INVALID_LEVEL,
        ]
    ),
)
async def create_correction(
    correction: CorrectionCreate,
    user: UserDep,
) -> CorrectionDocument:
    """Creates a correction note referring to a specific content"""

    # check if the resource this content belongs to is readable by user
    resource_doc = await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == correction.resource_id,
        await ResourceBaseDocument.access_conditions_read(user),
        with_children=True,
    )
    if not resource_doc:
        raise errors.E_404_RESOURCE_NOT_FOUND

    # get location, check if it is valid
    location_doc = await LocationDocument.get(correction.location_id)
    if not location_doc:
        raise errors.E_404_CONTENT_NOT_FOUND
    if (
        resource_doc.level != location_doc.level
        or resource_doc.text_id != location_doc.text_id
    ):
        raise errors.E_400_INVALID_REQUEST_DATA

    # construct full label
    location_labels = [location_doc.label]
    parent_location_id = location_doc.parent_id
    while parent_location_id:
        parent_location = await LocationDocument.get(parent_location_id)
        location_labels.insert(0, parent_location.label)
        parent_location_id = parent_location.parent_id

    # create correction
    correction_doc = await CorrectionDocument(
        resource_id=correction.resource_id,
        location_id=correction.location_id,
        position=location_doc.position,
        note=correction.note,
        user_id=user.id,
        date=datetime.now(UTC),
        location_labels=location_labels,
    ).create()

    # notify the resource's owner (or admins if it's public) of the new correction
    msg_specific_attrs = {
        "from_user_name": user.name if "name" in user.public_fields else user.username,
        "correction_note": correction.note,
        "text_slug": (await TextDocument.get(resource_doc.text_id)).slug,
        "resource_id": resource_doc.id,
        "resource_title": pick_translation(resource_doc.title),
    }
    if user.id != resource_doc.owner_id:
        to_user: UserDocument = await UserDocument.get(resource_doc.owner_id)
        if (
            to_user
            and TemplateIdentifier.EMAIL_NEW_CORRECTION.value
            in to_user.user_notification_triggers
        ):
            await send_notification(
                to_user,
                TemplateIdentifier.EMAIL_NEW_CORRECTION,
                **msg_specific_attrs,
            )

    return correction_doc


@router.get(
    "/{resourceId}",
    response_model=list[CorrectionRead],
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_404_RESOURCE_NOT_FOUND,
        ]
    ),
)
async def get_corrections(
    resource_id: Annotated[PydanticObjectId, Path(alias="resourceId")],
    user: UserDep,
) -> list[CorrectionDocument]:
    """Returns a list of all corrections for a specific resource"""
    # check if the requested resource is owned by this user
    resource_doc = await ResourceBaseDocument.get(
        resource_id,
        with_children=True,
    )
    if not resource_doc or (user.id != resource_doc.owner_id and not user.is_superuser):
        raise errors.E_404_RESOURCE_NOT_FOUND
    # return all corrections for the resource
    return await CorrectionDocument.find(
        CorrectionDocument.resource_id == resource_id,
    ).to_list()


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=errors.responses(
        [
            errors.E_404_NOT_FOUND,
        ]
    ),
)
async def delete_correction(
    correction_id: Annotated[PydanticObjectId, Path(alias="id")],
    user: UserDep,
) -> None:
    """Deletes a specific correction note"""
    # get correction
    correction_doc = await CorrectionDocument.get(correction_id)
    # check if correction exists
    if not correction_doc:
        raise errors.E_404_NOT_FOUND
    # check if the requested resource is writable by this user
    resource_doc = await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == correction_doc.resource_id,
        await ResourceBaseDocument.access_conditions_write(user),
        with_children=True,
    )
    if not resource_doc:
        raise errors.E_404_NOT_FOUND
    # delete correction
    await correction_doc.delete()
