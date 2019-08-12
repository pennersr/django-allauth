# -*- coding: utf-8 -*-
from allauth.socialaccount.tests import OAuthTestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import OpenStreetMapProvider


class OpenStreetMapTests(OAuthTestsMixin, TestCase):
    provider_id = OpenStreetMapProvider.id

    def get_mocked_response(self):
        return [MockedResponse(200, r"""<?xml version="1.0" encoding="UTF-8"?>
<osm version="0.6" generator="OpenStreetMap server" copyright="OpenStreetMap and contributors" attribution="http://www.openstreetmap.org/copyright" license="http://opendatacommons.org/licenses/odbl/1-0/">
<user id="1" display_name="Steve" account_created="2005-09-13T15:32:57Z">
  <description></description>
  <contributor-terms agreed="true"/>
  <img href="https://secure.gravatar.com/avatar.jpg"/>
  <roles>
  </roles>
  <changesets count="899"/>
  <traces count="21"/>
  <blocks>
    <received count="0" active="0"/>
  </blocks>
</user>
</osm>
""")]  # noqa

    def test_login(self):
        account = super(OpenStreetMapTests, self).test_login()
        osm_account = account.get_provider_account()
        self.assertEqual(osm_account.get_username(),
                         'Steve')
        self.assertEqual(osm_account.get_avatar_url(),
                         'https://secure.gravatar.com/avatar.jpg')
        self.assertEqual(osm_account.get_profile_url(),
                         'https://www.openstreetmap.org/user/Steve')
