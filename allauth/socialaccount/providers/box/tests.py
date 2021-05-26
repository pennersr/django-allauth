# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import BoxOAuth2Provider


class BoxOAuth2Tests(OAuth2TestsMixin, TestCase):
    provider_id = BoxOAuth2Provider.id

    def get_mocked_response(self):
        return [
            MockedResponse(
                200,
                """{
          "type": "user",
          "id": "1185237519",
          "name": "Balls Johnson",
          "login": "balls@example.com",
          "created_at": "2017-02-18T21:16:39-08:00",
          "modified_at": "2017-02-18T21:19:11-08:00",
          "language": "en",
          "timezone": "America/Los_Angeles",
          "space_amount": 10737418240,
          "space_used": 0,
          "max_upload_size": 2147483648,
          "status": "active",
          "job_title": "",
          "phone": "123-345-5555",
          "address": "",
          "avatar_url": "https://app.box.com/api/avatar/large/1185237519"
        }""",
            )
        ]
