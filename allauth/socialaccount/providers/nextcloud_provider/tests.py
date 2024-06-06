from django.test.utils import override_settings

from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import NextCloudProvider


@override_settings(
    SOCIALACCOUNT_PROVIDERS={"nextcloud": {"SERVER": "https://nextcloud.example.org"}}
)
class NextCloudTests(OAuth2TestsMixin, TestCase):
    provider_id = NextCloudProvider.id

    def get_login_response_json(self, with_refresh_token=True):
        return (
            super(NextCloudTests, self)
            .get_login_response_json(with_refresh_token=with_refresh_token)
            .replace("uid", "user_id")
        )

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """<?xml version="1.0"?>
<ocs>
 <meta>
  <status>ok</status>
  <statuscode>100</statuscode>
  <message>OK</message>
  <totalitems></totalitems>
  <itemsperpage></itemsperpage>
 </meta>
 <data>
  <enabled>1</enabled>
  <id>batman</id>
  <storageLocation>/var/www/html/data/batman</storageLocation>
  <lastLogin>1553946472000</lastLogin>
  <backend>Database</backend>
  <subadmin/>
  <quota>
   <free>1455417655296</free>
   <used>467191265</used>
   <total>1455884846561</total>
   <relative>0.03</relative>
   <quota>-3</quota>
  </quota>
  <email>batman@wayne.com</email>
  <displayname>batman</displayname>
  <phone>7351857301</phone>
  <address>BatCave, Gotham City</address>
  <website>https://batman.org</website>
  <twitter>@the_batman</twitter>
  <groups>
   <element>admin</element>
  </groups>
  <language>fr</language>
  <locale>fr_FR</locale>
  <backendCapabilities>
   <setDisplayName>1</setDisplayName>
   <setPassword>1</setPassword>
  </backendCapabilities>
 </data>
</ocs>
""",
        )
