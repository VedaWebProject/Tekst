from tekst.utils import strings


def test_cleanup_spaces_multiline():
    assert (
        strings.cleanup_spaces_multiline(" Foo  Bar\n\n\nBaz\n\n\n") == "Foo Bar\n\nBaz"
    )


def test_cleanup_spaces_oneline():
    assert strings.cleanup_spaces_oneline(" Foo  Bar\n\n\nBaz\n\n\n") == "Foo Bar Baz"
