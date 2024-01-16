import json

from tempfile import NamedTemporaryFile
from typing import Annotated

from beanie import PydanticObjectId
from beanie.exceptions import DocumentNotFound
from beanie.operators import In
from bson.errors import InvalidId
from fastapi import (
    APIRouter,
    Body,
    File,
    HTTPException,
    Path,
    Query,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from pydantic import ValidationError
from starlette.background import BackgroundTask

from tekst.auth import OptionalUserDep, SuperuserDep, UserDep
from tekst.logging import log
from tekst.models.exchange import ResourceDataImportResponse, ResourceImportData
from tekst.models.node import NodeDocument
from tekst.models.resource import ResourceBaseDocument
from tekst.models.text import TextDocument
from tekst.models.unit import UnitBaseDocument
from tekst.models.user import UserDocument, UserRead, UserReadPublic
from tekst.resources import (
    AnyResourceCreateBody,
    AnyResourceRead,
    AnyResourceReadBody,
    AnyResourceUpdateBody,
    get_resource_template_readme,
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
    resource.shared_read = []
    resource.shared_write = []
    # find document model for this resource type, instantiate, create
    resource_doc = (
        await resource_types_mgr.get(resource.resource_type)
        .resource_model()
        .document_model()
        .model_from(resource)
        .create()
    )
    return await preprocess_resource_read(resource_doc, user)


@router.post(
    "/{id}/version",
    response_model=AnyResourceReadBody,
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_201_CREATED: {"description": "Created"}},
)
async def create_resource_version(
    user: UserDep, resource_id: Annotated[PydanticObjectId, Path(alias="id")]
) -> AnyResourceRead:
    resource_doc: ResourceBaseDocument = await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == resource_id,
        await ResourceBaseDocument.access_conditions_read(user),
        with_children=True,
    )
    if not resource_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource with ID {resource_id} does not exist",
        )
    if resource_doc.original_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Resource with ID {resource_id} is "
                "already a version of another resource"
            ),
        )
    # generate version title suffix
    version_title_suffix = " v" + str(
        await ResourceBaseDocument.find(
            ResourceBaseDocument.original_id == resource_id,
            with_children=True,
        ).count()
        + 2
    )
    version_title = (
        resource_doc.title[0 : 64 - len(version_title_suffix)] + version_title_suffix
    )
    version_doc = (
        await resource_types_mgr.get(resource_doc.resource_type)
        .resource_model()
        .document_model()
        .model_from(
            resource_doc.model_copy(
                update={
                    ResourceBaseDocument.id: None,
                    ResourceBaseDocument.title: version_title,
                    ResourceBaseDocument.original_id: resource_doc.id,
                    ResourceBaseDocument.owner_id: user.id,
                    ResourceBaseDocument.proposed: False,
                    ResourceBaseDocument.public: False,
                    ResourceBaseDocument.shared_read: [],
                    ResourceBaseDocument.shared_write: [],
                }
            )
        )
        .create()
    )
    return await preprocess_resource_read(version_doc, user)


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
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource {resource_id} doesn't exist",
        )
    # only allow shares modification for owner or superuser
    if not user.is_superuser and resource_doc.owner_id != user.id:
        updates.shared_read = resource_doc.shared_read
        updates.shared_write = resource_doc.shared_write
    # conditionally force certain updates
    if resource_doc.public:
        updates.shared_read = []
        updates.shared_write = []
    # if the updates contain user shares, check if they are valid
    if updates.shared_read or updates.shared_write:
        for user_id in updates.shared_read + updates.shared_write:
            if not await UserDocument.find_one(UserDocument.id == user_id).exists():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Shared-with user {user_id} doesn't exist",
                )
    # update document with reduced updates
    await resource_doc.apply_updates(
        updates,
        exclude={
            "public",
            "proposed",
            "text_id",
            "owner_id",
            "level",
            "resource_type",
        },
    )
    return await preprocess_resource_read(resource_doc, user)


@router.get(
    "", response_model=list[AnyResourceReadBody], status_code=status.HTTP_200_OK
)
async def find_resources(
    user: OptionalUserDep,
    text_id: Annotated[
        PydanticObjectId,
        Query(alias="txt", description="ID of text to find resources for"),
    ] = None,
    level: Annotated[
        int, Query(alias="lvl", description="Structure level to find resources for")
    ] = None,
    resource_type: Annotated[
        str, Query(alias="type", description="Type of resources to find")
    ] = None,
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
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="You have no permission to delete this resource",
        )
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
    # turn versions of this resource into original resources
    await ResourceBaseDocument.find(
        ResourceBaseDocument.original_id == resource_id,
        with_children=True,
    ).set({ResourceBaseDocument.original_id: None})
    # delete units belonging to the resource
    await UnitBaseDocument.find(
        UnitBaseDocument.resource_id == resource_id,
        with_children=True,
    ).delete()
    # delete resource itself
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
        raise HTTPException(status.HTTP_403_FORBIDDEN)
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
        raise HTTPException(status.HTTP_403_FORBIDDEN)
    if resource_doc.public:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Resource with ID {resource_id} already public",
        )
    if resource_doc.original_id:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Cannot propose a version of another resource for publication",
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
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, detail="Not allowed to unpropose this resource"
        )
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
    if resource_doc.original_id:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Cannot publish a version of another resource",
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


@router.get("/{id}/template", status_code=status.HTTP_200_OK)
async def get_resource_template(
    user: UserDep,
    resource_id: Annotated[PydanticObjectId, Path(alias="id")],
) -> dict:
    resource_doc = await ResourceBaseDocument.get(
        resource_id,
        with_children=True,
    )
    if not resource_doc:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail=f"Resource with ID {resource_id} doesn't exist",
        )
    if not await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == resource_id,
        await ResourceBaseDocument.access_conditions_write(user),
        with_children=True,
    ).exists():
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="You have no permission to access this resource",
        )
    text_doc = await TextDocument.get(resource_doc.text_id)

    # import unit type for the requested resource
    template = resource_types_mgr.get(
        resource_doc.resource_type
    ).prepare_import_template()
    # apply data from resource instance
    template["resourceId"] = str(resource_doc.id)
    template["_resourceTitle"] = resource_doc.title
    # add resource template README text
    template["__README"] = get_resource_template_readme()

    # construct labels of all nodes on the resource's level
    node_locations = await NodeDocument.get_node_locations(
        text_id=text_doc.id,
        for_level=resource_doc.level,
        loc_delim=text_doc.loc_delim,
    )

    # fill in unit templates with IDs and some informational fields
    template["units"] = [
        dict(
            nodeId=str(node.id),
            _position=node.position,
            _location=node_locations.get(str(node.id)),
        )
        for node in await NodeDocument.find(
            NodeDocument.text_id == resource_doc.text_id,
            NodeDocument.level == resource_doc.level,
        )
        .sort(+NodeDocument.position)
        .to_list()
    ]

    # create temporary file and stream it as a file response
    tempfile = NamedTemporaryFile(mode="w")
    tempfile.write(json.dumps(template, indent=2, sort_keys=True))
    tempfile.flush()

    # prepare headers
    filename = f"{text_doc.slug}_resource_{resource_doc.id}" "_template.json"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}

    log.debug(f"Serving resource template as temporary file {tempfile.name}")
    return FileResponse(
        path=tempfile.name,
        headers=headers,
        media_type="application/json",
        background=BackgroundTask(tempfile.close),
    )


@router.post("/{id}/import", status_code=status.HTTP_201_CREATED)
async def import_resource_data(
    user: UserDep,
    resource_id: Annotated[PydanticObjectId, Path(alias="id")],
    file: Annotated[
        UploadFile, File(description="JSON file containing the resource data")
    ],
) -> ResourceDataImportResponse:
    # test upload file MIME type
    if not file.content_type.lower() == "application/json":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file MIME type (must be 'application/json')",
        )

    # check if resource exists
    if not await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == resource_id, with_children=True
    ).exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not find resource with ID {resource_id}",
        )

    # check if user has permission to write to this resource, if so, fetch from DB
    resource = await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == resource_id,
        await ResourceBaseDocument.access_conditions_write(user),
        with_children=True,
    )
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You have no permission to write to this resource",
        )

    # validate import file format
    try:
        structure_def = ResourceImportData.model_validate_json(await file.read())
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Import data is not valid JSON ({str(ve)})",
        )

    # check if resource_id matches the one in the import file
    if str(resource_id) != str(structure_def.resource_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resource ID in import file does not match resource ID in URL",
        )

    # find units that already exist and have to be updated instead of created
    try:
        existing_units_dict = {
            str(unit_doc.node_id): unit_doc
            for unit_doc in await UnitBaseDocument.find(
                UnitBaseDocument.resource_id == resource.id,
                In(
                    UnitBaseDocument.node_id,
                    [
                        PydanticObjectId(unit_data.get("nodeId", ""))
                        for unit_data in structure_def.units
                    ],
                ),
                with_children=True,
            ).to_list()
        }
    except InvalidId as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid nodeId value: {str(e)}",
        )

    # create lists of validated unit updates/creates depending on whether they exist
    units = {
        "updates": [],
        "creates": [],
    }
    update_model = (
        resource_types_mgr.get(resource.resource_type).unit_model().update_model()
    )
    create_model = (
        resource_types_mgr.get(resource.resource_type).unit_model().create_model()
    )
    for unit_data in structure_def.units:
        is_update = str(unit_data.get("nodeId", "")) in existing_units_dict
        try:
            units["updates" if is_update else "creates"].append(
                (update_model if is_update else create_model)(
                    resource_id=resource.id,
                    resource_type=resource.resource_type,
                    **unit_data,
                )
            )
        except ValidationError as ve:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid unit data: {str(ve)}",
            )

    # a sacrifice for the GC
    structure_def = None

    # process updates to existing units
    updated_count = 0
    errors_count = 0
    for update in units["updates"]:
        unit_doc = existing_units_dict.get(str(update.node_id))
        if unit_doc:
            try:
                await unit_doc.apply_updates(
                    update, exclude={"id", "resource_id", "node_id", "resource_type"}
                )
                updated_count += 1
            except (ValueError, DocumentNotFound) as e:
                print(e)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
                errors_count += 1
        else:
            errors_count += 1

    # process new units
    unit_document_model = (
        resource_types_mgr.get(resource.resource_type).unit_model().document_model()
    )
    # get node IDs from target level to check if the ones in new units are valid
    existing_node_ids = {
        n.id
        for n in await NodeDocument.find(
            NodeDocument.text_id == resource.text_id,
            NodeDocument.level == resource.level,
        ).to_list()
    }
    # filter out units that reference non-existent node IDs
    units["creates"] = [u for u in units["creates"] if u.node_id in existing_node_ids]

    # insert new units
    if len(units["creates"]):
        insert_many_result = await UnitBaseDocument.insert_many(
            [unit_document_model.model_from(c) for c in units["creates"]], ordered=False
        )
        created_count = len(insert_many_result.inserted_ids)
        errors_count += len(units["creates"]) - created_count
    else:
        created_count = 0

    return ResourceDataImportResponse(
        updated=updated_count, created=created_count, errors=errors_count
    )
