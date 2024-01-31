import bleach

from pydantic import BaseModel


_ALLOWED_TAGS = frozenset(
    {
        "a", "abbr", "acronym", "address", "article", "b", "blockquote", "br",
        "caption", "center", "cite", "code", "col", "colgroup", "data", "datalist",
        "dd", "del", "details", "dfn", "div", "dl", "dt", "em", "figcaption",
        "figure", "h1", "h2", "h3", "h4", "h5", "h6", "hr", "i", "img", "kbd",
        "label", "legend", "li", "mark", "multicol", "ol", "p", "pre", "q", "s",
        "section", "small", "spacer", "span", "strike", "strong", "sub", "summary",
        "sup", "table", "tbody", "td", "tfoot", "th", "thead", "time", "tr", "u", "ul"
    }
)  # fmt: skip

_ALLOWED_ATTRIBUTES = {
    "*": ["id"],
    "img": ["src", "alt", "title", "width", "height"],
    "a": ["href", "alt", "title", "target", "rel"],
}


def sanitize_user_html(html: str | None) -> str:
    if html is None:
        return None
    return bleach.clean(
        html,
        tags=_ALLOWED_TAGS,
        attributes=_ALLOWED_ATTRIBUTES,
        strip=True,
        strip_comments=False,
    )


def sanitize_user_model_html(
    models: BaseModel | list[BaseModel],
) -> BaseModel | list[BaseModel]:
    """
    Sanitizes HTML in user models.
    Only operates on fields explicitly named 'html'.
    """
    passed_list = True
    if not isinstance(models, list):
        passed_list = False
        models = [models]
    for model in models:
        if getattr(model, "html", None):
            model.html = sanitize_user_html(model.html)
    return models if passed_list else models[0]


def sanitize_user_dict_html(
    data: dict | list[dict],
) -> dict | list[dict]:
    """
    Sanitizes HTML in data dicts.
    Only operates on properties explicitly named 'html'.
    """
    passed_list = True
    if not isinstance(data, list):
        passed_list = False
        data = [data]
    for d in data:
        if "html" in d and d["html"]:
            d["html"] = sanitize_user_html(d["html"])
    return data if passed_list else data[0]
