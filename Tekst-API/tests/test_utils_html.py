from pydantic import BaseModel
from tekst.utils import html


class Model(BaseModel):
    html: str


def test_sanitize_user_html():
    assert html.sanitize_html() is None
    assert (
        html.sanitize_html("<p>FOO</p><script>alert('!!')</script>")
        == "<p>FOO</p>alert('!!')"
    )
    assert html.sanitize_html("<p onclick=\"alert('!!')\">FOO</p>") == "<p>FOO</p>"
    assert html.sanitize_model_html(Model(html="<p>FOO</p>")).html == "<p>FOO</p>"
    assert (
        html.sanitize_model_html(Model(html="<p onclick=\"alert('!!')\">FOO</p>")).html
        == "<p>FOO</p>"
    )
    assert (
        html.sanitize_dict_html({"html": "<p onclick=\"alert('!!')\">FOO</p>"})["html"]
        == "<p>FOO</p>"
    )
