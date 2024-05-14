from tekst.utils import strings


def test_cleanup_spaces_multiline():
    assert (
        strings.cleanup_spaces_multiline(" Foo \n \n\t\n Bar  Bar\n\n\nBaz\n\n\n")
        == "Foo\n\nBar Bar\n\nBaz"
    )


def test_cleanup_spaces_oneline():
    assert (
        strings.cleanup_spaces_oneline(" Foo \n \n\t\n Bar  Bar\n\n\nBaz\n\n\n")
        == "Foo Bar Bar Baz"
    )
