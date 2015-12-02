# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from allauth.socialaccount.tests import create_oauth2_tests
from allauth.tests import MockedResponse
from allauth.socialaccount.providers import registry

from .provider import BitbucketOAuth2Provider


class BitbucketOAuth2Tests(create_oauth2_tests(registry.by_id(
        BitbucketOAuth2Provider.id))):
    def get_mocked_response(self):
        return [MockedResponse(200, """
            {
                "created_on": "2011-12-20T16:34:07.132459+00:00",
                "display_name": "tutorials account",
                "links": {
                    "avatar": {
                        "href": "https://bitbucket-assetroot.s3.amazonaws.com/c/photos/2013/Nov/25/tutorials-avatar-1563784409-6_avatar.png"
                    },
                    "followers": {
                        "href": "https://api.bitbucket.org/2.0/users/tutorials/followers"
                    },
                    "following": {
                        "href": "https://api.bitbucket.org/2.0/users/tutorials/following"
                    },
                    "html": {
                        "href": "https://bitbucket.org/tutorials"
                    },
                    "repositories": {
                        "href": "https://api.bitbucket.org/2.0/repositories/tutorials"
                    },
                    "self": {
                        "href": "https://api.bitbucket.org/2.0/users/tutorials"
                    }
                },
                "location": "Santa Monica, CA",
                "type": "user",
                "username": "tutorials",
                "uuid": "{c788b2da-b7a2-404c-9e26-d3f077557007}",
                "website": "https://tutorials.bitbucket.org/"
            }
        """)]
