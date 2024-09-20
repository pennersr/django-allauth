import json
import time
from importlib import import_module
from urllib.parse import parse_qs, urlparse

from django.conf import settings
from django.test.utils import override_settings
from django.urls import reverse
from django.utils.http import urlencode

import jwt

from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase, mocked_response

from .apple_session import APPLE_SESSION_COOKIE_NAME
from .client import jwt_encode
from .provider import AppleProvider


# Generated on https://mkjwk.org/, used to sign and verify the apple id_token
TESTING_JWT_KEYSET = {
    "p": (
        "4ADzS5jKx_kdQihyOocVS0Qwwo7m0f7Ow56EadySJ-cmnwoHHF3AxgRaq-h-KwybSphv"
        "dc-X7NbS79-b9dumHKyt1MeVLAsDZD1a-uQCEneY1g9LsQkscNr7OggcpvMg5UUFwv6A"
        "kavu8cB0iyhNdha5_AWX27K5lNebvpaXEJ8"
    ),
    "kty": "RSA",
    "q": (
        "yy5UvMjrvZyO1Os_nxXIugCa3NyWOkC8oMppPvr1Bl5AnF_xwXN2n9ozPd9Nb3Q3n-om"
        "NgLayyUxhwIjWDlI67Vbx-ESuff8ZEBKuTK0Gdmr4C_QU_j0gvvNMNJweSPxDdRmIUgO"
        "njTVNWmdqFTZs43jXAT4J519rgveNLAkGNE"
    ),
    "d": (
        "riPuGIDde88WS03CVbo_mZ9toFWPyTxvuz8VInJ9S1ZxULo-hQWDBohWGYwvg8cgfXck"
        "cqWt5OBqNvPYdLgwb84uVi2JeEHmhcQSc_x0zfRTau5HVE2KdR-gWxQjPWoaBHeDVqwo"
        "PKaU2XYxa-gYDXcuSJWHz3BX13oInDEFCXr6VwiLiwLBFsb63EEHwyWXJbTpoar7AARW"
        "kz76qtngDkk4t9gk_Q0L1y1qf1GeWiAL7xWb-bdptma4-1ui-R2219-1ONEZ41v_jsIS"
        "_z8ooXmVCbUsHV4Z1UDpRvpORVE3u57WK3qXUdAtZsXjaIwkdItbDmL1jFUgefwfO91Y"
        "YQ"
    ),
    "e": "AQAB",
    "use": "sig",
    "kid": "testkey",
    "qi": (
        "R0Hu4YmpHzw3SKWGYuAcAo6B97-JlN2fXiTjZ2g8eHGQX7LSoKEu0Hmu5hcBZYSgOuor"
        "IPsPUu3mNtx3pjLMOaJRk34VwcYu7h23ogEKGcPUt1c4tTotFDdw8WFptDOw4ow31Tml"
        "BPExLqzzGjJeQSNULB1bExuuhYMWx6wBXo8"
    ),
    "dp": (
        "WBaHlnbjZ3hDVTzqjrGIYizSr-_aPUJitPKlR6wBncd8nJYo7bLAmB4mOewXkX5HozIG"
        "wuF78RsZoFLi1fAmhqgxQ7eopcU-9DBcksUPO4vkgmlJbrkYzNiQauW9vrllekOGXIQQ"
        "szhVoqP4MLEMpR-Sy9S3PyItcKbJDE3T4ik"
    ),
    "alg": "RS256",
    "dq": (
        "Ar5kbIw2CsBzeVKX8FkF9eUOMk9URAMdyPoSw8P1zRk2vCXbiOY7Qttad8ptLEUgfytV"
        "SsNtGvMsoQsZWRak8nHnhGJ4s0QzB1OK7sdNgU_cL1HV-VxSSPaHhdJBrJEcrzggDPEB"
        "KYfDHU6Iz34d1nvjBxoWE8rfqJsGbCW4xxE"
    ),
    "n": (
        "sclLPioUv4VOcOZWAKoRhcvwIH2jOhoHhSI_Cj5c5zSp7qaK8jCU6T7-GObsgrhpty-k"
        "26ZuqRdgu9d-62WO8OBGt1e0wxbTh128-nTTrOESHUlV_K1wpJmXOxNpJiybcgzZNbAm"
        "ACmsHfxZvN9bt7gKPXxf3-_zFAf12PbYMrOionAJ1N_4HxL7fz3xkr5C87Av06QNilIC"
        "-mA-4n9Eqw_R2DYNpE3RYMdWtwKqBwJC8qs3677RpG9vcc-yZ_97pEiytd2FBJ8uoTwH"
        "d3DHJB8UVgBSh1kMUpSdoM7HxVzKx732nx6Kusln79LrsfOzrXF4enkfKJYI40-uwT95"
        "zw"
    ),
}


# Mocked version of the test data from https://appleid.apple.com/auth/keys
KEY_SERVER_RESP_JSON = json.dumps(
    {
        "keys": [
            {
                "kty": TESTING_JWT_KEYSET["kty"],
                "kid": TESTING_JWT_KEYSET["kid"],
                "use": TESTING_JWT_KEYSET["use"],
                "alg": TESTING_JWT_KEYSET["alg"],
                "n": TESTING_JWT_KEYSET["n"],
                "e": TESTING_JWT_KEYSET["e"],
            }
        ]
    }
)


def sign_id_token(payload):
    """
    Sign a payload as apple normally would for the id_token.
    """
    signing_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(TESTING_JWT_KEYSET))
    return jwt_encode(
        payload,
        signing_key,
        algorithm="RS256",
        headers={"kid": TESTING_JWT_KEYSET["kid"]},
    )


@override_settings(
    SOCIALACCOUNT_STORE_TOKENS=False,
    SOCIALACCOUNT_PROVIDERS={
        "apple": {
            "APP": {
                "client_id": "app123id",
                "key": "apple",
                "secret": "dummy",
                "settings": {
                    "certificate_key": """-----BEGIN PRIVATE KEY-----
MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQg2+Eybl8ojH4wB30C
3/iDkpsrxuPfs3DZ+3nHNghBOpmhRANCAAQSpo1eQ+EpNgQQyQVs/F27dkq3gvAI
28m95JEk26v64YAea5NTH56mru30RDqTKPgRVi5qRu3XGyqy3mdb8gMy
-----END PRIVATE KEY-----
""",
                },
            }
        }
    },
)
class AppleTests(OAuth2TestsMixin, TestCase):
    provider_id = AppleProvider.id

    def get_apple_id_token_payload(self):
        now = int(time.time())
        return {
            "iss": "https://appleid.apple.com",
            "aud": "app123id",  # Matches `setup_app`
            "exp": now + 60 * 60,
            "iat": now,
            "sub": "000313.c9720f41e9434e18987a.1218",
            "at_hash": "CkaUPjk4MJinaAq6Z0tGUA",
            "email": "test@privaterelay.appleid.com",
            "email_verified": "true",
            "is_private_email": "true",
            "auth_time": 1234345345,  # not converted automatically by pyjwt
        }

    def test_verify_token(self):
        id_token = sign_id_token(self.get_apple_id_token_payload())
        with mocked_response(self.get_mocked_response()):
            sociallogin = self.provider.verify_token(None, {"id_token": id_token})
            assert sociallogin.user.email == "test@privaterelay.appleid.com"

    def get_login_response_json(self, with_refresh_token=True):
        """
        `with_refresh_token` is not optional for apple, so it's ignored.
        """
        id_token = sign_id_token(self.get_apple_id_token_payload())

        return json.dumps(
            {
                "access_token": "testac",  # Matches OAuth2TestsMixin value
                "expires_in": 3600,
                "id_token": id_token,
                "refresh_token": "testrt",  # Matches OAuth2TestsMixin value
                "token_type": "Bearer",
            }
        )

    def get_mocked_response(self):
        """
        Apple is unusual in that the `id_token` contains all the user info
        so no profile info request is made. However, it does need the
        public key verification, so this mocked response is the public
        key request in order to verify the authenticity of the id_token.
        """
        return MockedResponse(
            200, KEY_SERVER_RESP_JSON, {"content-type": "application/json"}
        )

    def get_expected_to_str(self):
        return "A B"

    def get_complete_parameters(self, auth_request_params):
        """
        Add apple specific response parameters which they include in the
        form_post response.

        https://developer.apple.com/documentation/sign_in_with_apple/sign_in_with_apple_js/incorporating_sign_in_with_apple_into_other_platforms
        """
        params = super().get_complete_parameters(auth_request_params)
        params.update(
            {
                "id_token": sign_id_token(self.get_apple_id_token_payload()),
                "user": json.dumps(
                    {
                        "email": "private@appleid.apple.com",
                        "name": {
                            "firstName": "A",
                            "lastName": "B",
                        },
                    }
                ),
            }
        )
        return params

    def login(self, resp_mock, process="login", with_refresh_token=True):
        resp = self.client.post(
            reverse(self.provider.id + "_login")
            + "?"
            + urlencode(dict(process=process))
        )
        p = urlparse(resp["location"])
        q = parse_qs(p.query)
        complete_url = reverse(self.provider.id + "_callback")
        self.assertGreater(q["redirect_uri"][0].find(complete_url), 0)
        response_json = self.get_login_response_json(
            with_refresh_token=with_refresh_token
        )
        with mocked_response(
            MockedResponse(200, response_json, {"content-type": "application/json"}),
            resp_mock,
        ):
            resp = self.client.post(
                complete_url,
                data=self.get_complete_parameters(q),
            )
            assert reverse("apple_finish_callback") in resp.url

            # Follow the redirect
            resp = self.client.get(resp.url)

        return resp

    def test_authentication_error(self):
        """Override base test because apple posts errors"""
        resp = self.client.post(
            reverse(self.provider.id + "_callback"),
            data={"error": "misc", "state": "testingstate123"},
        )
        assert reverse("apple_finish_callback") in resp.url
        # Follow the redirect
        resp = self.client.get(resp.url)

        self.assertTemplateUsed(
            resp,
            "socialaccount/authentication_error.%s"
            % getattr(settings, "ACCOUNT_TEMPLATE_EXTENSION", "html"),
        )

    def test_apple_finish(self):
        resp = self.login(self.get_mocked_response())

        # Check request generating the response
        finish_url = reverse("apple_finish_callback")
        self.assertEqual(resp.request["PATH_INFO"], finish_url)
        self.assertTrue("state" in resp.request["QUERY_STRING"])
        self.assertTrue("code" in resp.request["QUERY_STRING"])

        # Check have cookie containing apple session
        self.assertTrue(APPLE_SESSION_COOKIE_NAME in self.client.cookies)

        # Session should have been cleared
        apple_session_cookie = self.client.cookies.get(APPLE_SESSION_COOKIE_NAME)
        engine = import_module(settings.SESSION_ENGINE)
        SessionStore = engine.SessionStore
        apple_login_session = SessionStore(apple_session_cookie.value)
        self.assertEqual(len(apple_login_session.keys()), 0)

        # Check cookie path was correctly set
        self.assertEqual(apple_session_cookie.get("path"), finish_url)
