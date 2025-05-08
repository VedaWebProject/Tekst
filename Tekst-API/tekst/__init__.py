from importlib import metadata


_package_metadata = metadata.metadata(__package__)

# whyyyyy
_project_urls = {
    entry.split(", ")[0]: entry.split(", ")[1]
    for entry in _package_metadata.get_all("Project-URL", failobj="")
}

package_metadata = dict(
    version=_package_metadata["Version"],
    description=_package_metadata["Summary"],
    license=_package_metadata["License-Expression"],
    license_url=_project_urls["license"],
    website=_project_urls["repository"],
    documentation=_project_urls["documentation"],
)

__version__ = package_metadata["version"]

del metadata, _package_metadata
