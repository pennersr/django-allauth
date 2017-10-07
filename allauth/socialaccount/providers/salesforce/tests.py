# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from allauth.socialaccount.providers import registry
from allauth.socialaccount.tests import create_oauth2_tests
from allauth.tests import MockedResponse

from .provider import SalesforceProvider


class SalesforceTests(create_oauth2_tests(registry.by_id(
        SalesforceProvider.id))):

    def get_mocked_response(self,
                            last_name='Penners',
                            first_name='Raymond',
                            name='Raymond Penners',
                            email='raymond.penners@gmail.com',
                            verified_email=True):
        userinfo = USERINFO_RESPONSE.format(
            org_id="00Dxx00000000000A0",
            user_id="005xx000000aWwRQAU",
            vip="https://test.salesforce.com",
            nickname="test-ooi2xhmjteep",
            first_name=first_name,
            last_name=last_name,
            my_domain="https://fun.cs46.my.salesforce.com",
            content_domain="https://fun--c.cs46.content.force.com",
            verified_email=repr(verified_email).lower(),
            email=email,
            active="true",
            is_app_installed="true"
        )
        return MockedResponse(200, userinfo)


USERINFO_RESPONSE = """
{{
    "sub": "{vip}/id/{org_id}/{user_id}",
    "user_id": "{user_id}",
    "organization_id": "{org_id}",
    "preferred_username": "{nickname}@sample_-_dev_workspace.net",
    "nickname": "{nickname}",
    "name": "{first_name} {last_name}",
    "email": "{email}",
    "email_verified": {verified_email},
    "given_name": "{first_name}",
    "family_name": "{last_name}",
    "zoneinfo": "America/Los_Angeles",
    "photos": {{
        "picture": "{content_domain}/profilephoto/005/F",
        "thumbnail": "{content_domain}/profilephoto/005/T"
    }},
    "profile": "{my_domain}/{user_id}",
    "picture": "{content_domain}/profilephoto/005/F",
    "address": {{"country": "US"}},
    "urls": {{"custom_domain": "{my_domain}"}},
    "active": {active},
    "user_type": "STANDARD",
    "language": "en_US",
    "locale": "en_US",
    "utcOffset": -28800000,
    "updated_at": "2017-10-05T20:39:02.000+0000",
    "is_app_installed": {is_app_installed}
}}
"""
