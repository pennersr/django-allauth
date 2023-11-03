import json

from django.test import override_settings

import pytest

from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.amazon_cognito.provider import (
    AmazonCognitoProvider,
)
from allauth.socialaccount.providers.amazon_cognito.utils import (
    convert_to_python_bool_if_value_is_json_string_bool,
)
from allauth.socialaccount.providers.amazon_cognito.views import (
    AmazonCognitoOAuth2Adapter,
)
from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase


def _get_mocked_claims():
    return {
        "sub": "4993b410-8a1b-4c36-b843-a9c1a697e6b7",
        "given_name": "John",
        "family_name": "Doe",
        "email": "jdoe@example.com",
        "username": "johndoe",
    }


@override_settings(
    SOCIALACCOUNT_PROVIDERS={
        "amazon_cognito": {"DOMAIN": "https://domain.auth.us-east-1.amazoncognito.com"}
    }
)
class AmazonCognitoTestCase(OAuth2TestsMixin, TestCase):
    provider_id = AmazonCognitoProvider.id

    def get_mocked_response(self):
        mocked_payload = json.dumps(_get_mocked_claims())

        return MockedResponse(status_code=200, content=mocked_payload)

    @override_settings(SOCIALACCOUNT_PROVIDERS={"amazon_cognito": {}})
    def test_oauth2_adapter_raises_if_domain_settings_is_missing(
        self,
    ):
        mocked_response = self.get_mocked_response()

        with self.assertRaises(
            ValueError,
            msg=AmazonCognitoOAuth2Adapter.DOMAIN_KEY_MISSING_ERROR,
        ):
            self.login(mocked_response)

    def test_saves_email_as_verified_if_email_is_verified_in_cognito(
        self,
    ):
        mocked_claims = _get_mocked_claims()
        mocked_claims["email_verified"] = True
        mocked_payload = json.dumps(mocked_claims)
        mocked_response = MockedResponse(status_code=200, content=mocked_payload)

        self.login(mocked_response)

        user_id = SocialAccount.objects.get(uid=mocked_claims["sub"]).user_id
        email_address = EmailAddress.objects.get(user_id=user_id)

        self.assertEqual(email_address.email, mocked_claims["email"])
        self.assertTrue(email_address.verified)

    def test_provider_slug_replaces_underscores_with_hyphens(self):
        self.assertTrue("_" not in self.provider.get_slug())


@pytest.mark.parametrize(
    "input,output",
    [
        (True, True),
        ("true", True),
        ("false", False),
        (False, False),
    ],
)
def test_convert_bool(input, output):
    assert convert_to_python_bool_if_value_is_json_string_bool(input) == output
