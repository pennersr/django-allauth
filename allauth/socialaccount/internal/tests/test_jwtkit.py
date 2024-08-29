from datetime import timedelta

from django.utils import timezone

from allauth.socialaccount.internal.jwtkit import verify_and_decode
from allauth.socialaccount.providers.apple.client import jwt_encode
from allauth.socialaccount.providers.oauth2.client import OAuth2Error


def test_verify_and_decode(enable_cache):
    now = timezone.now()
    payload = {
        "iss": "https://accounts.google.com",
        "azp": "client_id",
        "aud": "client_id",
        "sub": "108204268033311374519",
        "hd": "example.com",
        "locale": "en",
        "iat": now,
        "jti": "a4e9b64d5e31da48a2037216e4ba9a5f5f4f50a0",
        "exp": now + timedelta(hours=1),
    }
    id_token = jwt_encode(payload, "secret")
    for attempt in range(2):
        try:
            verify_and_decode(
                credential=id_token,
                keys_url="/",
                issuer=payload["iss"],
                audience=payload["aud"],
                lookup_kid=False,
                verify_signature=False,
            )
            assert attempt == 0
        except OAuth2Error:
            assert attempt == 1
