import re

from tekst import __version__
from tekst.db.migrations import _all_migrations


# taken from https://github.com/pypa/packaging/blob/24.1/src/packaging/version.py#L117
_PEP440_VERSION_PATTERN = r"""
    v?
    (?:
        (?:(?P<epoch>[0-9]+)!)?                           # epoch
        (?P<release>[0-9]+(?:\.[0-9]+)*)                  # release segment
        (?P<pre>                                          # pre-release
            [-_\.]?
            (?P<pre_l>alpha|a|beta|b|preview|pre|c|rc)
            [-_\.]?
            (?P<pre_n>[0-9]+)?
        )?
        (?P<post>                                         # post release
            (?:-(?P<post_n1>[0-9]+))
            |
            (?:
                [-_\.]?
                (?P<post_l>post|rev|r)
                [-_\.]?
                (?P<post_n2>[0-9]+)?
            )
        )?
        (?P<dev>                                          # dev release
            [-_\.]?
            (?P<dev_l>dev)
            [-_\.]?
            (?P<dev_n>[0-9]+)?
        )?
    )
    (?:\+(?P<local>[a-z0-9]+(?:[-_\.][a-z0-9]+)*))?       # local version
"""

_PEP440_VERSION_REGEX = re.compile(
    r"^\s*" + _PEP440_VERSION_PATTERN + r"\s*$",
    re.VERBOSE | re.IGNORECASE,
)


def test_version_pep440():
    assert bool(re.match(_PEP440_VERSION_REGEX, __version__))


def test_migration_versions_pep440():
    for migration_version in _all_migrations():
        assert bool(re.match(_PEP440_VERSION_REGEX, str(migration_version)))
