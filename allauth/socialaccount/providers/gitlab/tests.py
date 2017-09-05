# -*- coding: utf-8 -*-
from allauth.socialaccount.providers.gitlab.provider import GitLabProvider
from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase


class GitLabTests(OAuth2TestsMixin, TestCase):
    provider_id = GitLabProvider.id

    def get_mocked_response(self):
        return MockedResponse(200, """
            {
                "avatar_url": "https://secure.gravatar.com/avatar/123",
                "bio": "",
                "can_create_group": "true",
                "can_create_project": "true",
                "color_scheme_id": 2,
                "created_at": "2015-12-14T23:40:33+0100",
                "current_sign_in_at": "2015-12-14T23:40:33+0100",
                "email": "mr.bob@gitlab.example.com",
                "id": 2,
                "identities": [],
                "is_admin": "false",
                "linkedin": "",
                "name": "Mr Bob",
                "private_token": "123",
                "projects_limit": 10,
                "skype": "mr.bob",
                "state": "active",
                "theme_id": 6,
                "twitter": "mrbob",
                "two_factor_enabled": "false",
                "username": "mr.bob",
                "web_url": "https://gitlab.example.com/u/mr.bob",
                "website_url": "https://example.com"
            }
        """)
