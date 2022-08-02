from textrig.config import Config


def test_config(app):
    config = Config(app_name="a", db_host="b", db_port=1, db_user="c", db_pass="d")
    assert config.app_name == "a"
    assert config.get_db_uri() == "mongodb://c:d@b:1"
