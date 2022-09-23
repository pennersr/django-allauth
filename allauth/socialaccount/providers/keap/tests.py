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
            }"""
        )

    def get_login_response_json(self, with_refresh_token=True):
        return """
        {
            "scope": "full|cb262.infusionsoft.com",
            "access_token": "testac",
            "token_type": "bearer",
            "expires_in": 86399,
            "refresh_token": "testrf"
        }"""
