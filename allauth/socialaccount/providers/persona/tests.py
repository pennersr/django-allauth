from django.test.utils import override_settings
from django.core.urlresolvers import reverse

from allauth.utils import get_user_model
from allauth.tests import TestCase, patch

SOCIALACCOUNT_PROVIDERS = {'persona':
                           {'AUDIENCE': 'https://www.example.com:433'}}


class PersonaTests(TestCase):

    @override_settings(SOCIALACCOUNT_PROVIDERS=SOCIALACCOUNT_PROVIDERS)
    def test_login(self):
        with patch('allauth.socialaccount.providers.persona.views'
                   '.requests') as requests_mock:
            requests_mock.post.return_value.json.return_value = {
                'status': 'okay',
                'email': 'persona@mail.com'
            }

            resp = self.client.post(reverse('persona_login'),
                                    dict(assertion='dummy'))
            self.assertRedirects(resp, '/accounts/profile/',
                                 fetch_redirect_response=False)
            get_user_model().objects.get(email='persona@mail.com')
