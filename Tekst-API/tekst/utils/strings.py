import re


def cleanup_spaces_multiline(string: str | None) -> str | None:
    """Reduces excessive newline chars and whitespaces and strips whitespaces"""
    if string is None:
        return None
    string = re.sub(r"[\n\r]{3,}", "\n\n", string)
    string = re.sub(r"[\t ]+", " ", string)
    return string.strip()


def cleanup_spaces_oneline(string: str | None) -> str | None:
    """Replaces any number of newlines with one whitespace and strips whitespaces"""
    if string is None:
        return None
    return re.sub(r"[\n\r\t ]+", " ", string).strip()
