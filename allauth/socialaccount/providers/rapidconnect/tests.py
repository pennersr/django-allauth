import time
from hashlib import md5

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.urls import reverse
from django.utils.http import urlencode

import jwt

from allauth.socialaccount import providers
from allauth.socialaccount.models import SocialApp, SocialToken
from allauth.tests import Mock, TestCase, patch

from . import provider, views


class RapidConnectTests(TestCase):

    secret_key = "SECRET123"

    def setUp(self):
        # workaround to create a session. see:
        # https://code.djangoproject.com/ticket/11475
        self.user = User.objects.create_user(
            "anakin", "skywalker@deathstar.example.com", "s1thrul3s"
        )
        self.client.login(username="anakin", password="s1thrul3s")

        self.provider = providers.registry.by_id(provider.RapidConnectProvider.id)
        app = SocialApp.objects.create(
            provider=self.provider.id,
            name=self.provider.id,
            client_id="https://rapidconnect.staging.tuakiri.ac.nz/jwt/authnrequest/research/d186lGxxUMoESD9rrAyJA",
            key=self.provider.id,
            secret=self.secret_key,
        )
        app.sites.add(Site.objects.get_current())
        self.app = app

    def get_rapidconnect_login_response(self):
        """
        Sample rapidconnect.lv response
        """
        now = int(time.time())
        token = {
            "iat": now,
            "nbf": now - 60,
            "exp": now + 42,
            "jti": "XBs8KeYbDrawTMWDN7M2TdvkMXpj_h8C",
            "typ": "authnresponse",
            "https://aaf.edu.au/attributes": {
                "cn": "Radomirs Cirskis",
                "displayname": "Radomirs Cirskis",
                "surname": "Cirskis",
                "givenname": "Radomirs",
                "mail": "radomirs.cirskis@aucklanduni.ac.nz",
                "edupersonorcid": "",
                "edupersonscopedaffiliation": "staff@virtualhome.test.tuakiri.ac.nz;member@virtualhome.test.tuakiri.ac.nz",
                "edupersonprincipalname": "",
                "edupersontargetedid": "https://rapidconnect.staging.tuakiri.ac.nz!https://127.0.0.1:8080!6dLjlotTdfoLct+ALy5NW0SF3dg=",
            },
            "iss": "https://rapidconnect.staging.tuakiri.ac.nz",
            "aud": "https://127.0.0.1:8080",
            "sub": "https://rapidconnect.staging.tuakiri.ac.nz!https://127.0.0.1:8080!6dLjlotTdfoLct+ALy5NW0SF3dg=",
        }
        return jwt.encode(token, key=self.secret_key).decode()

    def test_login_redirect(self):
        response = self.client.get(reverse(views.login))
        self.assertRedirects(
            response,
            self.app.client_id,
            fetch_redirect_response=False,
        )

    def test_callback(self):
        self.client.get(reverse(views.login))

        response_jwt = self.get_rapidconnect_login_response()

        response = self.client.post(reverse(views.callback), {"assertion": response_jwt})
        self.assertRedirects(response, "/accounts/profile/", fetch_redirect_response=False)

    def test_connect(self):
        self.client.get(reverse(views.login) + "?process=connect")

        response_jwt = self.get_rapidconnect_login_response()

        response = self.client.post(reverse(views.callback), {"assertion": response_jwt})
        self.assertRedirects(response, "/social/connections/", fetch_redirect_response=False)
