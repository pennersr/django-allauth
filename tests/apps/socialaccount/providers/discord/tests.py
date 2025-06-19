from django.contrib.auth import get_user_model
from django.test import TestCase

from allauth.account.models import EmailAddress
from allauth.account.utils import user_email, user_username
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.discord.provider import DiscordProvider
from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse


class DiscordTests(OAuth2TestsMixin, TestCase):
    provider_id = DiscordProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """{
            "id": "80351110224678912",
            "username": "nelly",
            "discriminator": "0",
            "global_name": "Nelly",
            "avatar": "8342729096ea3675442027381ff50dfe",
            "verified": true,
            "email": "nelly@example.com"
        }""",
        )

    def get_expected_to_str(self):
        return "Nelly"

    def test_display_name(self, multiple_login=False):
        email = "user@example.com"
        user = get_user_model()(is_active=True)
        user_email(user, email)
        user_username(user, "user")
        user.set_password("test")
        user.save()
        EmailAddress.objects.create(user=user, email=email, primary=True, verified=True)
        self.client.login(username=user.username, password="test")
        self.login(self.get_mocked_response(), process="connect")
        if multiple_login:
            self.login(
                self.get_mocked_response(),
                with_refresh_token=False,
                process="connect",
            )

        # get account
        sa = SocialAccount.objects.filter(user=user, provider=self.provider.id).get()
        # The following lines don't actually test that much, but at least
        # we make sure that the code is hit.
        provider_account = sa.get_provider_account()
        self.assertEqual(provider_account.to_str(), "Nelly")


class OldDiscordTests(DiscordTests, TestCase):
    provider_id = DiscordProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """{
            "id": "80351110224678912",
            "username": "Nelly",
            "discriminator": "1337",
            "avatar": "8342729096ea3675442027381ff50dfe",
            "verified": true,
            "email": "nelly@example.com"
        }""",
        )

    def get_expected_to_str(self):
        return "Nelly#1337"

    def test_display_name(self, multiple_login=False):
        email = "user@example.com"
        user = get_user_model()(is_active=True)
        user_email(user, email)
        user_username(user, "user")
        user.set_password("test")
        user.save()
        EmailAddress.objects.create(user=user, email=email, primary=True, verified=True)
        self.client.login(username=user.username, password="test")
        self.login(self.get_mocked_response(), process="connect")
        if multiple_login:
            self.login(
                self.get_mocked_response(),
                with_refresh_token=False,
                process="connect",
            )

        # get account
        sa = SocialAccount.objects.filter(user=user, provider=self.provider.id).get()
        # The following lines don't actually test that much, but at least
        # we make sure that the code is hit.
        provider_account = sa.get_provider_account()
        self.assertEqual(provider_account.to_str(), "Nelly#1337")
