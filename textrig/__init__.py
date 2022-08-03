from importlib import metadata

pkg_meta = {
    e[0].lower(): str(e[1]) for e in metadata.metadata(__package__).items()
    if e[0] in ("Version", "Summary", "Description", "License")
}

del metadata
