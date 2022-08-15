from textrig.config import DbConfig, TextRigConfig


def test_config(app, testing_config):
    config: TextRigConfig = testing_config()
    config.app_name = "a"
    assert config.app_name == "a"
    config.db = DbConfig(host="b", port=1, user="c", password="d")
    assert config.db.get_uri() == "mongodb://c:d@b:1"
