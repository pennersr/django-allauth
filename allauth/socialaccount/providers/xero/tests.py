import json
from django.contrib.auth import get_user_model
from django.utils.timezone import datetime, timedelta

from allauth.account.models import EmailAddress
from allauth.account.utils import user_email, user_username
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase
from allauth.socialaccount.providers.apple.client import jwt_encode

import jwt

from .provider import XeroProvider

TESTING_JWT_KEYSET = {
    "p": "3bHBzm9CAUjPOLHe5133Lcnl7OIvlwbSNo166pWNwJGSwlAj5NMhnvKZ7Qti5NBILfNmFS6Mm1QNH5yQN8f8Okin84sXcgdT9B9dNzudu0QcLMcKCHDViqNLbHdcDh0O9ZhOdtYz0wziwSgY4jWxL7XMNJXIcGIIsH2i50ol3-M",
    "kty": "RSA",
    "q": "wn99EF_GNulcQHRMTMsXFBCr523i5i_ZZI1v4EvpLpQc4tMZ2W-x9VNPeqImYD8I_N8uFHDlUsoucujBvilhqazmI1GIvDEy2N3-VlnTvozmkhHCPO9Sab5il4wsa_9hEgI1vMg-03V6Vsq4TCYfiD50MHeQLBdLcfBAECTl0Lk",
    "d": "ajHjxzabSfgwYIo192z1q8cFPATC8zGuRrd6XaXHmuSHO9-KldzV6-8nI2ggqd2AgNblglfljslGQIDoOjTzHyR6xBe6An8B6M9h8tJkeqX-JQG0DSGVEKIzDq4uksLQTK6mD7FF7MzkVoCMHz0XGQERyq0dmYCrM5pBRYYFWkxk62wcLBWyBo-TJB1A7PNwsjJySVUmvp5aaJ_yQwREvmFbsf1c9G6o2GnBcLDkYn5RV46rDJ4SIGOmfM5jTnji7SMEf9i_kTIKJvz8UNZHFNDl6ahy5p8KBWbvU8LH7m64zWPadvnHfXJGRJFf5roEKrW0h_5WptPoGmdpgdetgQ",
    "e": "AQAB",
    "use": "sig",
    "kid": "VfOUABw3YmRi0ri0DB1tz1XDZHnkqqhKHBbFz30T0D4",
    "qi": "giWWsyaNU4YOCSGSN0eS3nQIGE96B3CJq6HQ0Ftda8vcMIeZf3TAIgxB_kxN1urh3YwqYmr2W-2VxsaAM066rFumJmyyB5h83-huE9FwKKv6c4rrIWIpp653r5b4-9bVRx4xlpMdhTTQtcbvjj4QDOi-CrxicthyW5qMkR4PJtI",
    "dp": "I_LGDXZnCpRG3deh4HyRL0CU4wOOWfwGLEhmzRExKi-wz4d1Oo6t3ftS0GhPQfEwMxtLy1WAAVPwyNZ3YEQydzT-3vQH-jqL94L6d5FYM1yJAQ3JZ7L8PX3bJhx4teUqXtKyrnxvbOKjBlU9K7kvISBmm4RKO0b6R7wnpT-Vwqc",
    "alg": "RS256",
    "dq": "q-bH32f2pWO9IE5pfVnmLNrLRIFPkEjsJ74GCkStdHh9y0_uwcnBjGU0kturdVdhFzYd4P0jAfgl83OagPrMEY353W9bnZESMrCJ8UH1Lq4Tvzgo53hR65nUQ8MlI9KTtbn0SsTlGjnzhbAoEU2EgwNH5-pUp1NzX-GKjXo_ECk",
    "n": "qG8cW49nvecVapRWQI0Kz0H5-NNWCyGQbtyRdCFW_Vlgs9yNSr1PTsoLHkd_Pn1Di8SP5J_YMQ--PTTwdMGU91-Saq2QDD-q_veXVW0i7K9pyflQu6-FZDbwsKe1dgV4lkXNu0AFvM7jhYHTSqbGGNUxlmvN4cFH2GHeyl3xO1iB25rPS9jGUssIEOh4xWil6N0YiWorQedJqh-MAHuXe_dHSJHY8BOMyHr8rvzvVZ2360-690exinev3Z_gaZYa6fG5TVFrS9ErBQjmcG9LZM_Cuo2zDkmpkR5oTJqj83CFRlXbqOH2ZvcposS38zJg2WY1KJ_Tq80QoArwjVY7Cw",
}


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
                "x5t": "bodUTlQZd3BX3yyLdioJ4LxNrKU=",
                "x5c": [
                    "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqG8cW49nvecVapRWQI0Kz0H5+NNWCyGQbtyRdCFW/Vlgs9yNSr1PTsoLHkd/Pn1Di8SP5J/YMQ++PTTwdMGU91+Saq2QDD+q/veXVW0i7K9pyflQu6+FZDbwsKe1dgV4lkXNu0AFvM7jhYHTSqbGGNUxlmvN4cFH2GHeyl3xO1iB25rPS9jGUssIEOh4xWil6N0YiWorQedJqh+MAHuXe/dHSJHY8BOMyHr8rvzvVZ2360+690exinev3Z/gaZYa6fG5TVFrS9ErBQjmcG9LZM/Cuo2zDkmpkR5oTJqj83CFRlXbqOH2ZvcposS38zJg2WY1KJ/Tq80QoArwjVY7CwIDAQAB"
                ],
            }
        ]
    }
)


def sign_id_token(payload):
    """
    Sign a payload as apple normally would for the id_token.
    """
    signing_key = jwt.algorithms.RSAAlgorithm.from_jwk(
        json.dumps(TESTING_JWT_KEYSET)
    )
    return jwt_encode(
        payload,
        signing_key,
        algorithm="RS256",
        headers={"kid": TESTING_JWT_KEYSET["kid"]},
    )


class XeroTests(OAuth2TestsMixin, TestCase):
    provider_id = XeroProvider.id

    def get_xero_id_token_payload(self):
        now = datetime.now()
        client_id = "app123id"  # Matches `setup_app`
        payload = {
            "iss": "https://identity.xero.com",
            "aud": client_id,
            "sub": "108204268033311374519",
            "email": "raymond@example.com",
            "name": "Raymond Penners",
            "given_name": "Raymond",
            "family_name": "Penners",
            "xero_userid": "4eaedef4-ffba-4a9c-903f-c811ba031794",
            "iat": now,
            "exp": now + timedelta(hours=1),
        }
        # payload.update(self.identity_overwrites)
        return payload

    def get_login_response_json(self, with_refresh_token=True):
        rt = ""
        if with_refresh_token:
            rt = ',"refresh_token": "testrf"'
        return """{
            "id_token": "%s",
            "access_token":"%s",
            "token_type": "Bearer",
            "expires_in": 12345
            %s }""" % (
            sign_id_token(self.get_xero_id_token_payload()),
            sign_id_token(self.get_xero_id_token_payload()),
            rt,
        )

    def get_mocked_response(self):
        return [
            MockedResponse(
                200, KEY_SERVER_RESP_JSON, {"content-type": "application/json"}
            ),
            MockedResponse(
                200, KEY_SERVER_RESP_JSON, {"content-type": "application/json"}
            ),
            # MockedResponse(
            #     200,
            #     """{
            #     "id": "80351110224678912",
            #     "username": "nelly@example.com",
            #     "discriminator": "0",
            #     "global_name": "Nelly",
            #     "avatar": "8342729096ea3675442027381ff50dfe",
            #     "verified": true,
            #     "email":"nelly@example.com"
            # }""",
            # ),
        ]

    def test_display_name(self, multiple_login=False):
        email = "user@example.com"
        user = get_user_model()(is_active=True)
        user_email(user, email)
        user_username(user, "user")
        user.set_password("test")
        user.save()
        EmailAddress.objects.create(
            user=user, email=email, primary=True, verified=True
        )
        self.client.login(username=user.email_address, password="test")
        self.login(self.get_mocked_response(), process="connect")
        if multiple_login:
            self.login(
                self.get_mocked_response(),
                with_refresh_token=False,
                process="connect",
            )

        # get account
        sa = SocialAccount.objects.filter(
            user=user, provider=self.provider.id
        ).get()
        # The following lines don't actually test that much, but at least
        # we make sure that the code is hit.
        provider_account = sa.get_provider_account()
        self.assertEqual(provider_account.to_str(), "Nelly")
