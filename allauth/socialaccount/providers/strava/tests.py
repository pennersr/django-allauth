# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import StravaProvider


class StravaTests(OAuth2TestsMixin, TestCase):
    provider_id = StravaProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """{
                "id": 32641234,
                "username": null,
                "resource_state": 2,
                "firstname": "georges",
                "lastname": "camembert",
                "city": "London",
                "state": "England",
                "country": "United Kingdom",
                "sex": "M",
                "premium": false,
                "summit": false,
                "created_at": "2017-07-12T12:42:52Z",
                "updated_at": "2017-10-21T11:01:23Z",
                "badge_type_id": 0,
                "profile_medium": "avatar/athlete/medium.png",
                "profile": "avatar/athlete/large.png",
                "friend": null,
                "follower": null,
                "email": "bill@gmail.com"
            }""",
        )  # noqa

    def get_login_response_json(self, with_refresh_token=True):
        rt = ''
        if with_refresh_token:
            rt = ',"refresh_token": "testrf"'
        return """{
            "uid":"weibo",
            "access_token":"testac",
            "livemode": false,
            "token_type": "bearer",
            "strava_publishable_key": "pk_test_someteskey",
            "strava_user_id": "acct_sometestid",
            "scope": "read_write"
            %s }""" % rt
