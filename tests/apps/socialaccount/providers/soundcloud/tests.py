from django.test import TestCase

from allauth.socialaccount.providers.soundcloud.provider import SoundCloudProvider
from tests.apps.socialaccount.base import OAuth2TestsMixin
from tests.mocking import MockedResponse


class SoundCloudTests(OAuth2TestsMixin, TestCase):
    provider_id = SoundCloudProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
        {
           "website": null,
            "myspace_name": null,
            "public_favorites_count": 0,
            "followings_count": 1,
            "full_name": "",
            "urn": "soundcloud:users:22341947",
            "city": null,
            "track_count": 0,
            "playlist_count": 0,
            "discogs_name": null,
            "private_tracks_count": 0,
            "followers_count": 0,
            "online": true,
            "username": "user187631676",
            "description": null,
            "kind": "user",
            "website_title": null,
            "primary_email_confirmed": false,
            "permalink_url": "http://soundcloud.com/user187631676",
            "private_playlists_count": 0,
            "permalink": "user187631676",
            "country": null,
            "uri": "https://api.soundcloud.com/users/22341947",
            "avatar_url":
            "https://a1.sndcdn.com/images/default_avatar_large.png?4b4189b",
            "plan": "Free"
        }""",
        )

    def get_expected_to_str(self):
        return "user187631676"
