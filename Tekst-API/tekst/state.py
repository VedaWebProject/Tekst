from tekst.models.platform import PlatformStateDocument


async def get_state() -> PlatformStateDocument:
    return (
        await PlatformStateDocument.find_one() or await PlatformStateDocument().save()
    )


async def update_state(**kwargs) -> PlatformStateDocument:
    state = await get_state()
    for k, v in kwargs.items():
        setattr(state, k, v)
    return await state.replace()
