from django.test import TestCase

from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse

from .provider import EdxProvider


class EdxTests(OAuth2TestsMixin, TestCase):
    provider_id = EdxProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """{
"username":"krzysztof",
"bio":null,
"requires_parental_consent":true,
"language_proficiencies":[

],
"name":"Krzysztof Hoffmann",
"country":null,
"social_links":[

],
"is_active":true,
"profile_image":{
  "image_url_small":"http://draft.navoica.pl/static/images/profiles/default_30.png",
  "image_url_full":"http://draft.navoica.pl/static/images/profiles/default_500.png",
  "image_url_large":"http://draft.navoica.pl/static/images/profiles/default_120.png",
  "image_url_medium":"http://draft.navoica.pl/static/images/profiles/default_50.png",
  "has_image":false
},
"extended_profile":[

],
"year_of_birth":null,
"level_of_education":null,
"goals":"",
"accomplishments_shared":false,
"gender":null,
"date_joined":"2019-09-21T07:48:31Z",
"mailing_address":"",
"email":"krzysztof.hoffmann@opi.org.pl",
"account_privacy":"private"
}""",
        )

    def get_expected_to_str(self):
        return "krzysztof"
