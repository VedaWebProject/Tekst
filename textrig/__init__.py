from importlib import metadata


data = metadata.metadata(__package__)

# whyyyyy
license_url = [
    e for e in data.get_all("Project-URL", failobj="") if e.startswith("License")
][0].split(", ")[1]

pkg_meta = dict(
    version=data["Version"],
    description=data["Summary"],
    long_description=data["Description"],
    license=data["License"],
    license_url=license_url,
    website=data["Home-page"],
)

__version__ = pkg_meta["version"]

del metadata, data
