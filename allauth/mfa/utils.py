from allauth.mfa.adapter import get_adapter


def encrypt(text: str) -> str:
    return get_adapter().encrypt(text)


def decrypt(encrypted_text: str) -> str:
    return get_adapter().decrypt(encrypted_text)


def is_mfa_enabled(user, types=None) -> bool:
    return get_adapter().is_mfa_enabled(user, types=types)
