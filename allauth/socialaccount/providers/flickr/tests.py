from django.test import TestCase

from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.tests import OAuthTestsMixin
from allauth.tests import MockedResponse

from .provider import FlickrProvider


class FlickrTests(OAuthTestsMixin, TestCase):
    provider_id = FlickrProvider.id

    def get_mocked_response(self):
        #
        return [
            MockedResponse(
                200,
                r"""
 {"stat": "ok",
  "user": {
    "username": {
    "_content": "pennersr"},
    "id": "12345678@N00"}}
""",
            ),  # noqa
            MockedResponse(
                200,
                r"""
{"person": {"username": {"_content": "pennersr"}, "photosurl": {"_content":
 "http://www.flickr.com/photos/12345678@N00/"},
 "nsid": "12345678@N00",
 "path_alias": null, "photos": {"count": {"_content": 0},
 "firstdatetaken": {"_content": null}, "views": {"_content": "28"},
 "firstdate": {"_content": null}}, "iconserver": "0",
 "description": {"_content": ""}, "mobileurl": {"_content":
 "http://m.flickr.com/photostream.gne?id=6294613"},
 "profileurl": {
 "_content": "http://www.flickr.com/people/12345678@N00/"},
 "mbox_sha1sum": {"_content":
 "5e5b359c123e54f95236209c8808d607a5cdd21e"},
 "ispro": 0, "location": {"_content": ""},
 "id": "12345678@N00",
 "realname": {"_content": "raymond penners"},
 "iconfarm": 0}, "stat": "ok"}
""",
            ),
        ]  # noqa

    def get_expected_to_str(self):
        return "pennersr"

    def test_login(self):
        super().test_login()
        account = SocialAccount.objects.get(uid="12345678@N00")
        f_account = account.get_provider_account()
        self.assertEqual(account.user.first_name, "raymond")
        self.assertEqual(account.user.last_name, "penners")
        self.assertEqual(
            f_account.get_profile_url(),
            "http://www.flickr.com/people/12345678@N00/",
        )
        self.assertEqual(f_account.to_str(), "pennersr")


class FlickrWithoutRealNameTests(OAuthTestsMixin, TestCase):
    """Separate test for Flickr accounts without real names"""

    provider_id = FlickrProvider.id

    def get_mocked_response(self):
        #
        return [
            MockedResponse(
                200,
                r"""
 {"stat": "ok",
  "user": {
    "username": {
    "_content": "pennersr"},
    "id": "12345678@N00"}}
""",
            ),  # noqa
            MockedResponse(
                200,
                r"""
{"person": {"username": {"_content": "pennersr"}, "photosurl": {"_content":
 "http://www.flickr.com/photos/12345678@N00/"},
 "nsid": "12345678@N00",
 "path_alias": null, "photos": {"count": {"_content": 0},
 "firstdatetaken": {"_content": null}, "views": {"_content": "28"},
 "firstdate": {"_content": null}}, "iconserver": "0",
 "description": {"_content": ""}, "mobileurl": {"_content":
 "http://m.flickr.com/photostream.gne?id=6294613"},
 "profileurl": {
 "_content": "http://www.flickr.com/people/12345678@N00/"},
 "mbox_sha1sum": {"_content":
 "5e5b359c123e54f95236209c8808d607a5cdd21e"},
 "ispro": 0, "location": {"_content": ""},
 "id": "12345678@N00",
 "realname": {"_content": ""},
 "iconfarm": 0}, "stat": "ok"}
""",
            ),
        ]  # noqa

    def get_expected_to_str(self):
        return "pennersr"

    def test_login(self):
        super().test_login()
        account = SocialAccount.objects.get(uid="12345678@N00")
        f_account = account.get_provider_account()
        self.assertEqual(account.user.first_name, "")
        self.assertEqual(account.user.last_name, "")
        self.assertEqual(
            f_account.get_profile_url(),
            "http://www.flickr.com/people/12345678@N00/",
        )
        self.assertEqual(f_account.to_str(), "pennersr")
