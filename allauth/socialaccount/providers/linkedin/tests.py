# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from allauth.socialaccount.tests import OAuthTestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import LinkedInProvider


class LinkedInTests(OAuthTestsMixin, TestCase):
    provider_id = LinkedInProvider.id

    def get_mocked_response(self):
        return [
            MockedResponse(
                200,
                """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<person>
  <id>oKmTqN2ffc</id>
  <first-name>R@ymØnd</first-name>
  <last-name>Pènnèrs</last-name>
  <email-address>raymond.penners@example.com</email-address>
  <picture-url>http://m.c.lnkd.licdn.com/mpr/mprx/0_e0hbvSLc8QWo3ggPeVKqvaFR860d342Pogq4vakwx8IJOyR1XJrwRmr5mIx9C0DxWpGMsW9Lb8EQ</picture-url>
  <public-profile-url>http://www.linkedin.com/in/intenct</public-profile-url>
</person>
""",
            )
        ]
