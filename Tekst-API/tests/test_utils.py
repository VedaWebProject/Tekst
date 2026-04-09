import pytest

from tekst import html
from tekst.types import _cleanup_spaces_multiline, _cleanup_spaces_oneline
from tekst.utils import ensure


def test_cleanup_spaces_multiline():
    assert (
        _cleanup_spaces_multiline(" Foo \n \n\t\n Bar  Bar\n\n\nBaz\n\n\n")
        == "Foo\n\nBar Bar\n\nBaz"
    )


def test_cleanup_spaces_oneline():
    assert (
        _cleanup_spaces_oneline(" Foo \n \n\t\n Bar  Bar\n\n\nBaz\n\n\n")
        == "Foo Bar Bar Baz"
    )


def test_get_html_text():
    assert html.get_html_text() is None
    assert html.get_html_text("<p>FOO</p>") == "FOO"


def test_sanitize_html():
    assert html.sanitize_html() is None
    assert (
        html.sanitize_html("<p>FOO</p><script>alert('!!')</script>")
        == "<p>FOO</p>alert('!!')"
    )
    assert html.sanitize_html("<p onclick=\"alert('!!')\">FOO</p>") == "<p>FOO</p>"


def test_force_html():
    assert html.force_html() is None
    html_str = "foo"
    assert html.force_html(html_str) == f"<p>{html_str}</p>"
    html_str = html.force_html(html_str)
    assert html.force_html(html_str) == html_str


def test_ensure():
    # None
    v = None
    with pytest.raises(ValueError):
        ensure(v)
    # falsy: empty string
    v = ""
    assert ensure(v) == ""
    with pytest.raises(ValueError):
        ensure(v, strict=True)
    # falsy: empty list
    v = []
    assert isinstance(ensure(v), list)
    with pytest.raises(ValueError):
        ensure(v, strict=True)
    # falsy: empty dict
    v = {}
    assert isinstance(ensure(v), dict)
    with pytest.raises(ValueError):
        ensure(v, strict=True)
