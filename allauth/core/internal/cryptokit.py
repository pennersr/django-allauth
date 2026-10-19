import math
import secrets
import string
from typing import TypedDict

from django.utils.crypto import get_random_string


class UserCodeFormat(TypedDict, total=False):
    dashed: bool
    length: int
    numeric: bool


# https://datatracker.ietf.org/doc/html/rfc8628#section-6.1
_ALPHA_ALLOWED_CHARS = "BCDFGHJKLMNPQRSTVWXZ"


def generate_user_code(
    *,
    length: int | None = None,
    numeric: bool = False,
    allowed_chars: str | None = None,
    dashed: bool = True,
) -> str:
    """ """
    if not allowed_chars:
        if numeric:
            allowed_chars = string.digits
        else:
            allowed_chars = _ALPHA_ALLOWED_CHARS
    if length is None:
        length = 9 if numeric else 8
    code = get_random_string(length=length, allowed_chars=allowed_chars)
    if dashed:
        parts = 2 if length <= 8 else 3
        chunk = math.ceil(length / parts)
        code = "-".join(code[i : i + chunk] for i in range(0, length, chunk))
    return code


def normalize_user_code(code: str) -> str:
    """https://datatracker.ietf.org/doc/html/rfc8628#section-6.1

    When processing the inputted user code, the server should strip dashes and
    other punctuation that it added for readability (making the inclusion of
    such punctuation by the user optional).
    """
    return code.translate(
        str.maketrans("", "", string.punctuation + string.whitespace)
    ).lower()


def compare_user_code(*, actual: str, expected: str) -> bool:
    actual = normalize_user_code(actual)
    expected = normalize_user_code(expected)
    try:
        return bool(expected) and secrets.compare_digest(actual, expected)
    except TypeError:
        # secrets.compare_digest can throw:
        # TypeError: comparing strings with non-ASCII characters is not supported
        return False
