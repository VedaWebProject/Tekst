from pydantic import BaseModel
from tekst.utils import html


class Model(BaseModel):
    html: str


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
