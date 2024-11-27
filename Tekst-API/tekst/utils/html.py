import bleach


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


def get_html_text(html: str | None = None) -> str | None:
    if html is None:
        return None
    return bleach.clean(
        html,
        tags=set(),
        attributes=dict(),
        strip=True,
        strip_comments=True,
    )


def sanitize_html(html: str | None = None) -> str | None:
    if html is None:
        return None
    return bleach.clean(
        html,
        tags=_ALLOWED_TAGS,
        attributes=_ALLOWED_ATTRIBUTES,
        strip=True,
        strip_comments=False,
    )
