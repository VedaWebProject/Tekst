import re

from packaging.version import Version
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


def test_migration_sorting():
    from tekst.db.migrations import _sort_migrations

    migrations = {
        Version("10.12.4a0"): lambda: 6,
        Version("1.2.30"): lambda: 5,
        Version("0.1.0"): lambda: 2,
        Version("1.2.4"): lambda: 4,
        Version("0.1.0a1"): lambda: 1,
        Version("1.2.3"): lambda: 3,
        Version("0.1.0a0"): lambda: 0,
    }
    migration_results = [migrations[ver]() for ver in _sort_migrations(migrations)]
    assert migration_results == sorted(migration_results)
