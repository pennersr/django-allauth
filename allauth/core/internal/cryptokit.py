import string

from django.utils.crypto import get_random_string


def generate_user_code(length=6) -> str:
    forbidden_chars = "0OI18B2ZAEU"
    allowed_chars = string.ascii_uppercase + string.digits
    for ch in forbidden_chars:
        allowed_chars = allowed_chars.replace(ch, "")
    return get_random_string(length=length, allowed_chars=allowed_chars)


def compare_user_code(*, actual, expected) -> bool:
    actual = actual.replace(" ", "").lower()
    expected = expected.replace(" ", "").lower()
    return expected and actual == expected
