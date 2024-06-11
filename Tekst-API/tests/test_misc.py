from tekst.auth import _validate_required_password_chars


def test_password_chars_regex():
    # these should fail
    assert not _validate_required_password_chars("abcdemnbnbnb1")
    assert not _validate_required_password_chars("123456789p")
    assert not _validate_required_password_chars("foo1")
    assert not _validate_required_password_chars("Foo")
    assert not _validate_required_password_chars("1FOOOOOOOOO")
    # these should go through
    assert _validate_required_password_chars("kjhasaKJHKJ123312")
    assert _validate_required_password_chars("poiPOI098")
    assert _validate_required_password_chars("123foobAr")
    assert _validate_required_password_chars("1-2.3?f*o+obAr")
