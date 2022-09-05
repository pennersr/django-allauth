# -*- coding: utf-8 -*-
from allauth.socialaccount.providers.keap.provider import KeapProvider
from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase


class KeapTests(OAuth2TestsMixin, TestCase):
    provider_id = KeapProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """{
                    "email": "test@example.com",
                    "family_name": "LastName",
                    "given_name": "FirstName",
                    "global_user_id": 0,
                    "infusionsoft_id": "test@example.com",
                    "middle_name": "MiddleName",
                    "preferred_name": "FirstName LastName",
                    "sub": "0"
                }""",
        )
