import re


def cleanup_spaces_multiline(string: str | None) -> str | None:
    """Reduces excessive newline chars and whitespaces and strips whitespaces"""
    if string is None:
        return None
    string = str(string)
    string = re.sub(r"(\r\n|\r|\n)", "\n", string)  # normalize line breaks
    string = re.sub(r"[\t ]*\n[\t ]*", "\n", string)  # remove spaces around line breaks
    string = re.sub(r"\n{3,}", "\n\n", string)  # max. 2 consecutive line breaks
    string = re.sub(r"[\t ]+", " ", string)  # replace excessive whitespaces
    return string.strip()


def cleanup_spaces_oneline(string: str | None) -> str | None:
    """Replaces any number of newlines with one whitespace and strips whitespaces"""
    if string is None:
        return None
    # replace any sequence of spaces with one whitespace, return the result
    return re.sub(r"\s+", " ", str(string)).strip()
