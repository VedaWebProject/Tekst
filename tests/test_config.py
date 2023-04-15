from tekst.config import DbConfig, TekstConfig


def test_config():
    cfg: TekstConfig = TekstConfig()
    cfg.info.platform_name = "a"
    assert cfg.info.platform_name == "a"
    cfg.db = DbConfig(host="b", port=1, user="c", password="d")
    assert cfg.db.get_uri() == "mongodb://c:d@b:1"
    cfg.db.user = ""
    assert cfg.db.get_uri() == "mongodb://b:1"
