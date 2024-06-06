def test_cors_validator(config):
    split = config.cors.split_cors("*")
    assert len(split) == 1
    assert split[0] == "*"
    split = config.cors.split_cors("foo.com,bar.com")
    assert len(split) == 2
    assert split[0] == "foo.com"
    assert split[1] == "bar.com"
    cors_list = ["foo.com", "bar.com"]
    assert config.cors.split_cors(cors_list) == cors_list
