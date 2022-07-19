from textrig import __version__, main


def test_version():
    assert __version__ == "0.0.1"


def test_hello_world():
    assert main.hello_world()["version"] == __version__
