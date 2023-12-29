import pytest


def test_cors_validator(config):
    split = config.split_cors("*")
    assert len(split) == 1
    assert split[0] == "*"
    split = config.split_cors("foo.com,bar.com")
    assert len(split) == 2
    assert split[0] == "foo.com"
    assert split[1] == "bar.com"
    cors_list = ["foo.com", "bar.com"]
    assert config.split_cors(cors_list) == cors_list


def test_config_model_dump_kwargs(config):
    # kwargs 'include_keys_prefix' and 'include' are exclusive
    with pytest.raises(AttributeError):
        config.model_dump(include_keys_prefix="info", include={"foo", "bar"})
    # with 'include_keys_prefix'
    config_dump = config.model_dump(include_keys_prefix="info")
    assert len(config_dump) == 6
    assert config_dump.get("info_platform_name")
    # with 'include_keys_prefix' and 'strip_include_keys_prefix'
    config_dump = config.model_dump(
        include_keys_prefix="info_", strip_include_keys_prefix=True
    )
    assert len(config_dump) == 6
    assert config_dump.get("platform_name")
    # no 'include_keys_prefix'
    assert len(config.model_dump(include={"dev_mode"})) == 1
