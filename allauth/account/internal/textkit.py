def compare_code(*, actual, expected) -> bool:
    actual = actual.replace(" ", "").lower()
    expected = expected.replace(" ", "").lower()
    return expected and actual == expected
