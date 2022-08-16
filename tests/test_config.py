from textrig.config import DbConfig, TextRigConfig


def test_config(app, testing_config):
    cfg: TextRigConfig = testing_config()
    cfg.app_name = "a"
    assert cfg.app_name == "a"
    cfg.db = DbConfig(host="b", port=1, user="c", password="d")
    assert cfg.db.get_uri() == "mongodb://c:d@b:1"
    cfg.db.user = ""
    assert cfg.db.get_uri() == "mongodb://b:1"
