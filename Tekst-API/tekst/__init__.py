from importlib import metadata


_package_metadata = metadata.metadata(__package__)

# whyyyyy
_project_urls = _package_metadata.get_all("Project-URL", failobj="")
license_url = [e for e in _project_urls if e.startswith("License, ")][0].split(", ")[1]
documentation = [e for e in _project_urls if e.startswith("Documentation, ")][0].split(
    ", "
)[1]

package_metadata = dict(
    version=_package_metadata["Version"],
    description=_package_metadata["Summary"],
    license=_package_metadata["License"],
    license_url=license_url,
    website=_package_metadata["Home-page"],
    documentation=documentation,
)

__version__ = package_metadata["version"]

del metadata, _package_metadata
