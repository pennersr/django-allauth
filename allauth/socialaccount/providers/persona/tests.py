try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

from django.test import TestCase
from django.core.urlresolvers import reverse

from allauth.utils import get_user_model


class PersonaTests(TestCase):

    def test_login(self):
        with patch('allauth.socialaccount.providers.persona.views'
                   '.requests') as requests_mock:
            requests_mock.post.return_value.json.return_value = {
                'status': 'okay',
                'email': 'persona@mail.com'
            }
            resp = self.client.post(reverse('persona_login'),
                                    dict(assertion='dummy'))
            self.assertEqual('http://testserver/accounts/profile/',
                             resp['location'])
            get_user_model().objects.get(email='persona@mail.com')
