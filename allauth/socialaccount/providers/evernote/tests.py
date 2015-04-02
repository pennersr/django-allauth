# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from allauth.socialaccount.tests import create_oauth_tests
from allauth.tests import MockedResponse
from allauth.socialaccount.providers import registry

from .provider import EvernoteProvider


class EvernoteTests(create_oauth_tests(registry.by_id(EvernoteProvider.id))):

    def get_mocked_response(self):
        return []

    def get_access_token_response(self):
        return MockedResponse(
            200,
            'oauth_token=S%3Ds1%3AU%3D9876%3AE%3D999999b0c50%3AC%3D14c1f89dd18%3AP%3D81%3AA%3Dpennersr%3AV%3D2%3AH%3Ddeadf00dd2d6aba7b519923987b4bf77&oauth_token_secret=&edam_shard=s1&edam_userId=591969&edam_expires=1457994271824&edam_noteStoreUrl=https%3A%2F%2Fsandbox.evernote.com%2Fshard%2Fs1%2Fnotestore&edam_webApiUrlPrefix=https%3A%2F%2Fsandbox.evernote.com%2Fshard%2Fs1%2F',  # noqa
            {'content-type': 'text/plain'})
