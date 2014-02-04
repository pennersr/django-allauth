# -*- coding: utf-8 -*-
from allauth.socialaccount.tests import create_oauth_tests
from allauth.tests import MockedResponse
from allauth.socialaccount.providers import registry

from .provider import BitbucketProvider


class BitbucketTests(create_oauth_tests(registry.by_id(BitbucketProvider.id))):
    def get_mocked_response(self):
        # FIXME: Replace with actual/complete Bitbucket response
        return [MockedResponse(200, r"""
[{"active": true, "email": "raymond.penners@intenct.nl", "primary": true},
 {"active": true, "email": "raymond.penners@gmail.com", "primary": false},
 {"active": true,
  "email": "raymond.penners@jibecompany.com",
  "primary": false}]
        """),
                MockedResponse(200, r"""
{"repositories": [],
 "user": {"avatar": "https://secure.gravatar.com/avatar.jpg",
           "display_name": "pennersr",
           "first_name": "",
           "is_team": false,
           "last_name": "",
           "resource_uri": "/1.0/users/pennersr",
           "username": "pennersr"}}
 """)]  # noqa

    def test_login(self):
        account = super(BitbucketTests, self).test_login()
        bb_account = account.get_provider_account()
        self.assertEqual(bb_account.get_username(),
                         'pennersr')
        self.assertEqual(bb_account.get_avatar_url(),
                         'https://secure.gravatar.com/avatar.jpg')
        self.assertEqual(bb_account.get_profile_url(),
                         'http://bitbucket.org/pennersr')
