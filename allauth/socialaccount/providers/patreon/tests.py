from django.test import TestCase

from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse

from .provider import PatreonProvider


class PatreonTests(OAuth2TestsMixin, TestCase):
    provider_id = PatreonProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """{
        "data": {
            "relationships": {
                "pledges": {
                    "data": [{
                        "type": "pledge", "id": "123456"
                    }]
                }
            },
            "attributes": {
                "last_name": "Interwebs",
                "is_suspended": false,
                "has_password": true,
                "full_name": "John Interwebs",
                "is_nuked": false,
                "first_name": "John",
                "social_connections": {
                    "spotify": null,
                    "discord": null,
                    "twitter": null,
                    "youtube": null,
                    "facebook": null,
                    "deviantart": null,
                    "twitch": null
                },
                "twitter": null,
                "is_email_verified": true,
                "facebook_id": null,
                "email": "john@example.com",
                "facebook": null,
                "thumb_url": "https://c8.patreon.com/100/123456",
                "vanity": null,
                "about": null,
                "is_deleted": false,
                "created": "2017-05-05T05:16:34+00:00",
                "url": "https://www.patreon.com/user?u=123456",
                "gender": 0,
                "youtube": null,
                "discord_id": null,
                "image_url": "https://c8.patreon.com/400/123456",
                "twitch": null
            },
            "type": "user",
            "id": "123456"
        }
        }""",
        )  # noqa

    def get_expected_to_str(self):
        return "john@example.com"
