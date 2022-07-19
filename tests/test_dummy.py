from textrig import __version__, main


def test_holy_hand_grenade_of_antioch():
    count = 0
    for i in range(0, 3):
        count += 1
    assert count == 3, "Three shalt be the number thou shalt count."


def test_app_ref():
    assert main.hello_world()["version"] == __version__
