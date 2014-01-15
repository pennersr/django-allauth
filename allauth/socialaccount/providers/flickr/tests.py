# -*- coding: utf-8 -*-
from allauth.socialaccount.tests import create_oauth_tests
from allauth.tests import MockedResponse
from allauth.socialaccount.providers import registry

from .provider import FlickrProvider


class FlickrTests(create_oauth_tests(registry.by_id(FlickrProvider.id))):
    def get_mocked_response(self):
        #
        return [
            MockedResponse(200, r"""
 {"stat": "ok", "user": {"username": {"_content": "pennersr"}, "id": "12345678@N00"}}
"""),  # noqa
            MockedResponse(200, r"""
{"person": {"username": {"_content": "pennersr"}, "photosurl": {"_content": "http://www.flickr.com/photos/12345678@N00/"}, "nsid": "12345678@N00", "path_alias": null, "photos": {"count": {"_content": 0}, "firstdatetaken": {"_content": null}, "views": {"_content": "28"}, "firstdate": {"_content": null}}, "iconserver": "0", "description": {"_content": ""}, "mobileurl": {"_content": "http://m.flickr.com/photostream.gne?id=6294613"}, "profileurl": {"_content": "http://www.flickr.com/people/12345678@N00/"}, "mbox_sha1sum": {"_content": "5e5b359c123e54f95236209c8808d607a5cdd21e"}, "ispro": 0, "location": {"_content": ""}, "id": "12345678@N00", "realname": {"_content": "raymond penners"}, "iconfarm": 0}, "stat": "ok"}
""")]  # noqa

    def test_login(self):
        account = super(FlickrTests, self).test_login()
        f_account = account.get_provider_account()
        self.assertEqual(account.user.first_name,
                         'raymond')
        self.assertEqual(account.user.last_name,
                         'penners')
        self.assertEqual(f_account.get_profile_url(),
                         'http://www.flickr.com/people/12345678@N00/')
