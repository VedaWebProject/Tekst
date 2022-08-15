from textrig.config import TextRigConfig, DbConfig


def test_config(app):
    config = TextRigConfig(
        app_name="a",
        db=DbConfig(
            host="b",
            port=1,
            user="c",
            password="d"
        )
    )
    assert config.app_name == "a"
    assert config.db.get_db_uri() == "mongodb://c:d@b:1"
