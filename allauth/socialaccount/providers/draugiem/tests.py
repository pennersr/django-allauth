from hashlib import md5

from django.core.urlresolvers import reverse
from django.utils.http import urlencode

from allauth.socialaccount import providers
from allauth.socialaccount.models import SocialLogin, SocialToken
from allauth.utils import get_user_model
from allauth.tests import TestCase, Mock, patch

from . import views
from .provider import DraugiemProvider


class DraugiemTests(TestCase):
    fixtures = ['sites.json', 'auth.json', 'socialaccount.json']

    def get_draugiem_login_response(self):
        """
        Sample Draugiem.lv response
        """
        return {
            "apikey": "12345",
            "uid": "42",
            "users": {
                "42": {
                    "age": "266",
                    "imgl": "http://cdn.memegenerator.net/instances/500x/23395689.jpg",
                    "surname": "Skywalker",
                    "url": "/user/42/",
                    "imgi": "http://cdn.memegenerator.net/instances/500x/23395689.jpg",
                    "nick": "Sky Guy",
                    "created": "09.11.1812 11:26:15",
                    "deleted": "false",
                    "imgm": "http://cdn.memegenerator.net/instances/500x/23395689.jpg",
                    "sex": "M",
                    "type": "User_Default",
                    "uid": "42",
                    "place": "London",
                    "emailHash": "3f198f21434gfd2f2b4rs05939shk93f3815bc6aa",
                    "name": "Anakin",
                    "adult": "1",
                    "birthday": "1750-09-13",
                    "img": "http://cdn.memegenerator.net/instances/500x/23395689.jpg"
                }
            }
        }

    def get_socialaccount_app(self):
        """
        Returns SocialApp model
        """
        provider = providers.registry.by_id(DraugiemProvider.id)
        app = providers.registry.by_id(DraugiemProvider.id) \
                .get_app(reverse(views.login))
        return app

    def get_socialaccount(self, response, token):
        """
        Returns SocialLogin based on the data from the request
        """
        request = Mock()
        provider = providers.registry.by_id(DraugiemProvider.id)
        login = provider.sociallogin_from_response(request, response)
        login.token = token
        return login

    def mock_socialaccount_state(self):
        """
        SocialLogin depends on Session state - a tuple of request params and a random string
        """
        session = self.client.session
        session['socialaccount_state'] = ({
            'process': 'login',
            'scope': '',
            'auth_params': ''
        }, '12345')
        session.save()

    def test_login_redirect(self):
        response = self.client.get(reverse(views.login), follow=False, **{'HTTP_HOST': 'localhost'})
        app = self.get_socialaccount_app()
        redirect_url = 'http://localhost' + reverse(views.callback)
        redirect_url_hash = md5((app.secret + redirect_url).encode('utf-8')).hexdigest()
        params = {
            'app': app.client_id,
            'hash': redirect_url_hash,
            'redirect': redirect_url,
        }
        self.assertRedirects(response, '%s?%s' % (views.AUTHORIZE_URL, urlencode(params)), fetch_redirect_response=False)

    def test_callback_no_auth_status(self):
        response = self.client.get(reverse(views.callback))
        self.assertTemplateUsed(response, "socialaccount/authentication_error.html")

    def test_callback_invalid_auth_status(self):
        response = self.client.get(reverse(views.callback), {'dr_auth_status': 'fail'})
        self.assertTemplateUsed(response, "socialaccount/authentication_error.html")

    def test_callback(self):
        with patch('allauth.socialaccount.providers.draugiem.views.draugiem_complete_login') as draugiem_complete_login:
            self.mock_socialaccount_state()

            response_json = self.get_draugiem_login_response()

            app = self.get_socialaccount_app()
            token = SocialToken(app=app, token=response_json['apikey'])
            login = self.get_socialaccount(response_json, token)

            draugiem_complete_login.return_value = login

            response = self.client.get(reverse(views.callback), {'dr_auth_status': 'ok', 'dr_auth_code': '42'})
            self.assertRedirects(response, '/accounts/profile/', fetch_redirect_response=False)
