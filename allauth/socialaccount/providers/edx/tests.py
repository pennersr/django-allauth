from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import EdxProvider


class EdxTests(OAuth2TestsMixin, TestCase):
    provider_id = EdxProvider.id

    def get_mocked_response(self):
        return MockedResponse(200, """
        {'accomplishments_shared': False,
 'account_privacy': 'private',
 'bio': None,
 'country': None,
 'date_joined': '2019-09-21T07:48:31Z',
 'email': 'krzysztof.hoffmann@opi.org.pl',
 'extended_profile': [],
 'gender': None,
 'goals': '',
 'is_active': True,
 'language_proficiencies': [],
 'level_of_education': None,
 'mailing_address': '',
 'name': 'Krzysztof Hoffmann',
 'profile_image': {'has_image': False,
                   'image_url_full': 'http://draft.navoica.pl/static/images/profiles/default_500.png',
                   'image_url_large': 'http://draft.navoica.pl/static/images/profiles/default_120.png',
                   'image_url_medium': 'http://draft.navoica.pl/static/images/profiles/default_50.png',
                   'image_url_small': 'http://draft.navoica.pl/static/images/profiles/default_30.png'},
 'requires_parental_consent': True,
 'social_links': [],
 'username': 'krzysztof',
 'year_of_birth': None}""")
