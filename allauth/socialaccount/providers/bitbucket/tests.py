# -*- coding: utf-8 -*-
from allauth.socialaccount.tests import OAuthTestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import BitbucketProvider


class BitbucketTests(OAuthTestsMixin, TestCase):
    provider_id = BitbucketProvider.id

    def get_mocked_response(self):
        # FIXME: Replace with actual/complete Bitbucket response
        return [
            MockedResponse(
                200,
                r"""
[{"active": true, "email": "raymond.penners@example.com", "primary": true},
 {"active": true, "email": "raymond.penners@example.org", "primary": false}
]
        """,
            ),
            MockedResponse(
                200,
                r"""
{"repositories": [],
 "user": {"avatar": "https://secure.gravatar.com/avatar.jpg",
           "display_name": "pennersr",
           "first_name": "",
           "is_team": false,
           "last_name": "",
           "resource_uri": "/1.0/users/pennersr",
           "username": "pennersr"}}
 """,
            ),
        ]  # noqa

    def test_login(self):
        account = super(BitbucketTests, self).test_login()
        bb_account = account.get_provider_account()
        self.assertEqual(bb_account.get_username(), "pennersr")
        self.assertEqual(
            bb_account.get_avatar_url(),
            "https://secure.gravatar.com/avatar.jpg",
        )
        self.assertEqual(bb_account.get_profile_url(), "http://bitbucket.org/pennersr")
