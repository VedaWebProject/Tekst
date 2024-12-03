import pytest

from pydantic import ValidationError
from tekst.config import TekstConfig


def test_cors_validator():
    config = TekstConfig()
    split = config.cors.split_cors("*")
    assert len(split) == 1
    assert split[0] == "*"
    split = config.cors.split_cors("foo.com,bar.com")
    assert len(split) == 2
    assert split[0] == "foo.com"
    assert split[1] == "bar.com"
    cors_list = ["foo.com", "bar.com"]
    assert config.cors.split_cors(cors_list) == cors_list


def test_db_validators():
    config = TekstConfig()
    # DB name is not a string (will be forced)
    config.db.name = 12345
    assert config.db.name == "12345"
    # DB name contains invalid chars (expect error)
    with pytest.raises(ValueError):
        config.db.name = "foo?§bar"
    # DB host and password are encoded for use in URLs
    config.db.host = "foo/bar"
    assert config.db.host == r"foo%2Fbar"
    config.db.password = "foo/bar"
    assert config.db.password == r"foo%2Fbar"
    # pass None as DB host (should raise error)
    with pytest.raises(ValidationError):
        config.db.host = None


def test_es_validators():
    config = TekstConfig()
    # ES URL is URL-encoded
    config.es.host = "foo/bar"
    assert config.es.host == r"foo%2Fbar"
    # ES timeout_search_s as int is converted to time string (e.g. "60s")
    config.es.timeout_search_s = 60
    assert config.es.timeout_search_s == "60s"
    # correct ES timeout_search_s as str should be left untouched
    config.es.timeout_search_s = "40s"
    assert config.es.timeout_search_s == "40s"
    # invalid ES timeout_search_s as str should be the contained digits + "s"
    config.es.timeout_search_s = "foo4bar0s"
    assert config.es.timeout_search_s == "40s"
    # invalid ES timeout_search_s as str without digits should be "30s"
    config.es.timeout_search_s = "foobar"
    assert config.es.timeout_search_s == "30s"
    # pass None as ES host
    with pytest.raises(ValidationError):
        config.es.host = None


def test_temp_files_dir_validator():
    config = TekstConfig()
    # test if temp_files_dir is an existing, writable directory
    with pytest.raises(ValueError):
        config.temp_files_dir = "/foo/bar"
