import json

from tempfile import NamedTemporaryFile
from typing import Annotated

from beanie import PydanticObjectId
from beanie.operators import In
from fastapi import APIRouter, Body, HTTPException, Path, Query, status
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from tekst.auth import OptionalUserDep, SuperuserDep, UserDep
from tekst.logging import log
from tekst.models.node import NodeDocument
from tekst.models.resource import ResourceBaseDocument
from tekst.models.text import TextDocument
from tekst.models.unit import UnitBaseDocument
from tekst.models.user import UserDocument, UserRead, UserReadPublic
from tekst.resource_types import (
    AnyResourceCreateBody,
    AnyResourceRead,
    AnyResourceReadBody,
    AnyResourceUpdateBody,
    resource_types_mgr,
)


async def preprocess_resource_read(
    resource_doc: ResourceBaseDocument,
    for_user: UserRead | None = None,
) -> AnyResourceRead:
    # convert resource document to resource type's read model instance
    resource = (
        resource_types_mgr.get(resource_doc.resource_type)
        .resource_model()
        .read_model()(
            **resource_doc.model_dump(exclude=resource_doc.restricted_fields(for_user))
        )
    )
    # include writable flag
    resource.writable = bool(
        for_user
        and (
            for_user.is_superuser
            or (
                (
                    for_user.id == resource.owner_id
                    or for_user.id in resource.shared_write
                )
                and not resource.public
                and not resource.proposed
            )
        )
    )
    # include owner user data in each resource model (if an owner id is set)
    if resource.owner_id:
        resource.owner = UserReadPublic.model_from(
            await UserDocument.get(resource.owner_id)
        )
    # include shared-with user data in each resource model (if any)
    if for_user and (for_user.is_superuser or for_user.id == resource.owner_id):
        if resource.shared_read:
            resource.shared_read_users = await UserDocument.find(
                In(UserDocument.id, resource.shared_read)
            ).to_list()
        if resource.shared_write:
            resource.shared_write_users = await UserDocument.find(
                In(UserDocument.id, resource.shared_write)
            ).to_list()
    return resource


router = APIRouter(
    prefix="/resources",
    tags=["resources"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Not found"},
    },
)


@router.post(
    "",
    response_model=AnyResourceReadBody,
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_201_CREATED: {"description": "Created"}},
)
async def create_resource(
    resource: AnyResourceCreateBody, user: UserDep
) -> AnyResourceRead:
    text = await TextDocument.get(resource.text_id)
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Resource refers to non-existent text '{resource.text_id}'",
        )
    if resource.level > len(text.levels) - 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Text '{text.title}' only has {len(text.levels)} levels",
        )
    # force some values on creation
    resource.owner_id = user.id
    resource.proposed = False
    resource.public = False
    # find document model for this resource type, instantiate, create
    resource_doc = (
        await resource_types_mgr.get(resource.resource_type)
        .resource_model()
        .document_model()
        .model_from(resource)
        .create()
    )
    return await preprocess_resource_read(resource_doc, user)


@router.patch(
    "/{id}", response_model=AnyResourceReadBody, status_code=status.HTTP_200_OK
)
async def update_resource(
    resource_id: Annotated[PydanticObjectId, Path(alias="id")],
    updates: AnyResourceUpdateBody,
    user: UserDep,
) -> AnyResourceRead:
    resource_doc = await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == resource_id,
        await ResourceBaseDocument.access_conditions_write(user),
        with_children=True,
    )
    if not resource_doc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Resource {resource_id} doesn't exist / requires extra permissions",
        )
    # conditionally force certain updates
    if resource_doc.public:
        updates.shared_read = []
        updates.shared_write = []
    # only allow shares modification for owner or superuser
    if not user.is_superuser and resource_doc.owner_id != user.id:
        updates.shared_read = resource_doc.shared_read
        updates.shared_write = resource_doc.shared_write
    # update document with reduced updates
    await resource_doc.apply(
        updates.model_dump(
            exclude_unset=True,
            # force-keep non-updatable fields
            exclude={
                "public",
                "proposed",
                "text_id",
                "owner_id",
                "level",
                "resource_type",
            },
        )
    )
    return await preprocess_resource_read(resource_doc, user)


@router.get(
    "", response_model=list[AnyResourceReadBody], status_code=status.HTTP_200_OK
)
async def find_resources(
    user: OptionalUserDep,
    text_id: Annotated[PydanticObjectId, Query(alias="textId")],
    level: int = None,
    resource_type: Annotated[str, Query(alias="resourceType")] = None,
    limit: int = 4096,
) -> list[AnyResourceRead]:
    """
    Returns a list of all resources matching the given criteria.

    As the resulting list of resources may contain resources of different types, the
    returned resource objects cannot be typed to their precise resource type.
    """
    example = {"text_id": text_id}

    # add to example
    if level is not None:
        example["level"] = level
    if resource_type:
        example["resource_type"] = resource_type

    # query for resources the user is allowed to read and that belong to active texts
    resource_docs = (
        await ResourceBaseDocument.find(
            example,
            await ResourceBaseDocument.access_conditions_read(user),
            with_children=True,
        )
        .limit(limit)
        .to_list()
    )
    # return processed results
    return [
        await preprocess_resource_read(resource_doc, user)
        for resource_doc in resource_docs
    ]


@router.get("/{id}/template", status_code=status.HTTP_200_OK)
async def get_resource_template(
    user: UserDep,
    resource_id: Annotated[str, Path(alias="id")],
) -> dict:
    resource_doc = await ResourceBaseDocument.get(resource_id, with_children=True)
    if not resource_doc:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Resource with ID {resource_id} doesn't exist",
        )
    text_doc = await TextDocument.get(resource_doc.text_id)

    # import unit type for the requested resource
    template = resource_types_mgr.get(
        resource_doc.resource_type
    ).prepare_import_template()
    # apply data from resource instance
    template["resourceId"] = str(resource_doc.id)
    template["_level"] = resource_doc.level
    template["_title"] = resource_doc.title
    template["_description"] = resource_doc.description

    # generate unit template
    unit_template = {key: None for key in template["_unitSchema"]}

    # get IDs of all nodes on this structure level as a base for unit templates
    nodes = await NodeDocument.find(
        NodeDocument.text_id == resource_doc.text_id,
        NodeDocument.level == resource_doc.level,
    ).to_list()

    # fill in unit templates with IDs
    template["units"] = [dict(nodeId=str(node.id), **unit_template) for node in nodes]

    # create temporary file and stream it as a file response
    tempfile = NamedTemporaryFile(mode="w")
    tempfile.write(json.dumps(template, indent=2, sort_keys=True))
    tempfile.flush()

    # prepare headers
    filename = f"{text_doc.slug}_resource_{resource_doc.id}" "_template.json"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}

    log.debug(f"Serving resource template as temporary file {tempfile.name}")
    return FileResponse(
        tempfile.name,
        headers=headers,
        media_type="application/json",
        background=BackgroundTask(tempfile.close),
    )


@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=AnyResourceReadBody)
async def get_resource(
    user: OptionalUserDep,
    resource_id: Annotated[PydanticObjectId, Path(alias="id")],
) -> AnyResourceRead:
    resource_doc = await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == resource_id,
        await ResourceBaseDocument.access_conditions_read(user),
        with_children=True,
    )
    if not resource_doc:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail=f"No resource with ID {resource_id}"
        )
    return await preprocess_resource_read(resource_doc, user)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resource(
    user: UserDep, resource_id: Annotated[PydanticObjectId, Path(alias="id")]
) -> None:
    resource_doc = await ResourceBaseDocument.get(resource_id, with_children=True)
    if not resource_doc:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail=f"No resource with ID {resource_id}"
        )
    if not user.is_superuser and user.id != resource_doc.owner_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    if resource_doc.public:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a published resource",
        )
    if resource_doc.proposed:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a proposed resource",
        )
    # all fine
    # delete units
    await UnitBaseDocument.find(
        UnitBaseDocument.resource_id == resource_id,
        with_children=True,
    ).delete()
    # delete resource
    await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == resource_id,
        with_children=True,
    ).delete()


@router.post(
    "/{id}/transfer", response_model=AnyResourceReadBody, status_code=status.HTTP_200_OK
)
async def transfer_resource(
    user: UserDep,
    resource_id: Annotated[PydanticObjectId, Path(alias="id")],
    target_user_id: Annotated[PydanticObjectId, Body()],
) -> AnyResourceRead:
    resource_doc = await ResourceBaseDocument.get(resource_id, with_children=True)
    if not resource_doc:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail=f"No resource with ID {resource_id}"
        )
    if not user.is_superuser and user.id != resource_doc.owner_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    if resource_doc.public or resource_doc.proposed:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Resource with ID {resource_id} is "
                "published or proposed for publication"
            ),
        )
    if not await UserDocument.find_one(UserDocument.id == target_user_id).exists():
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail=f"No user with ID {target_user_id}"
        )
    if target_user_id == resource_doc.owner_id:
        return await preprocess_resource_read(resource_doc, user)
    # all fine, transfer resource and remove target user ID from resource shares
    await resource_doc.set(
        {
            ResourceBaseDocument.owner_id: target_user_id,
            ResourceBaseDocument.shared_read: [
                u_id
                for u_id in resource_doc.shared_read
                if str(u_id) != str(target_user_id)
            ],
            ResourceBaseDocument.shared_write: [
                u_id
                for u_id in resource_doc.shared_write
                if str(u_id) != str(target_user_id)
            ],
        }
    )
    return await preprocess_resource_read(resource_doc, user)


@router.post(
    "/{id}/propose", response_model=AnyResourceReadBody, status_code=status.HTTP_200_OK
)
async def propose_resource(
    user: UserDep, resource_id: Annotated[PydanticObjectId, Path(alias="id")]
) -> AnyResourceRead:
    resource_doc = await ResourceBaseDocument.get(resource_id, with_children=True)
    if not resource_doc:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail=f"No resource with ID {resource_id}"
        )
    if not user.is_superuser and user.id != resource_doc.owner_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    if resource_doc.public:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Resource with ID {resource_id} already public",
        )
    # all fine, propose resource
    await resource_doc.set(
        {
            ResourceBaseDocument.proposed: True,
            ResourceBaseDocument.shared_read: [],
            ResourceBaseDocument.shared_write: [],
        }
    )
    return await preprocess_resource_read(resource_doc, user)


@router.post(
    "/{id}/unpropose",
    response_model=AnyResourceReadBody,
    status_code=status.HTTP_200_OK,
)
async def unpropose_resource(
    user: UserDep, resource_id: Annotated[PydanticObjectId, Path(alias="id")]
) -> AnyResourceRead:
    resource_doc = await ResourceBaseDocument.get(resource_id, with_children=True)
    if not resource_doc:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail=f"No resource with ID {resource_id}"
        )
    if not user.is_superuser and user.id != resource_doc.owner_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    # all fine, unpropose resource
    await resource_doc.set(
        {
            ResourceBaseDocument.proposed: False,
            ResourceBaseDocument.public: False,
        }
    )
    return await preprocess_resource_read(resource_doc, user)


@router.post(
    "/{id}/publish", response_model=AnyResourceReadBody, status_code=status.HTTP_200_OK
)
async def publish_resource(
    user: SuperuserDep, resource_id: Annotated[PydanticObjectId, Path(alias="id")]
) -> AnyResourceRead:
    resource_doc = await ResourceBaseDocument.get(resource_id, with_children=True)
    if not resource_doc:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail=f"No resource with ID {resource_id}"
        )
    if not resource_doc.proposed:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Resource with ID {resource_id} is not proposed for publication",
        )
    # all fine, publish resource
    await resource_doc.set(
        {
            ResourceBaseDocument.public: True,
            ResourceBaseDocument.proposed: False,
            ResourceBaseDocument.owner_id: None,
            ResourceBaseDocument.shared_read: [],
            ResourceBaseDocument.shared_write: [],
        }
    )
    return await preprocess_resource_read(resource_doc, user)


@router.post(
    "/{id}/unpublish",
    response_model=AnyResourceReadBody,
    status_code=status.HTTP_200_OK,
)
async def unpublish_resource(
    user: SuperuserDep, resource_id: Annotated[PydanticObjectId, Path(alias="id")]
) -> AnyResourceRead:
    resource_doc = await ResourceBaseDocument.get(resource_id, with_children=True)
    if not resource_doc:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail=f"No resource with ID {resource_id}"
        )
    # all fine, unpublish resource
    await resource_doc.set(
        {
            ResourceBaseDocument.public: False,
            ResourceBaseDocument.proposed: False,
        }
    )
    return await preprocess_resource_read(resource_doc, user)
