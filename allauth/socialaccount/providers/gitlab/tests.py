# -*- coding: utf-8 -*-
from allauth.socialaccount.providers.gitlab.provider import GitLabProvider
from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase


class GitLabTests(OAuth2TestsMixin, TestCase):
    provider_id = GitLabProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
            {
                "avatar_url": "https://secure.gravatar.com/avatar/123",
                "bio": null,
                "can_create_group": true,
                "can_create_project": true,
                "color_scheme_id": 5,
                "confirmed_at": "2015-03-02T16:53:58.370Z",
                "created_at": "2015-03-02T16:53:58.885Z",
                "current_sign_in_at": "2018-06-12T18:44:49.985Z",
                "email": "mr.bob@gitlab.example.com",
                "external": false,
                "id": 2,
                "identities": [],
                "last_activity_on": "2018-06-11",
                "last_sign_in_at": "2018-05-31T14:59:44.527Z",
                "linkedin": "",
                "location": null,
                "name": "Mr Bob",
                "organization": null,
                "projects_limit": 10,
                "shared_runners_minutes_limit": 2000,
                "skype": "",
                "state": "active",
                "theme_id": 6,
                "twitter": "mrbob",
                "two_factor_enabled": true,
                "username": "mr.bob",
                "web_url": "https://gitlab.example.com/u/mr.bob",
                "website_url": ""
            }
        """,
        )
