from hashlib import md5
from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import RequestFactory
from django.urls import reverse
from django.utils.http import urlencode

from allauth import app_settings
from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken
from allauth.tests import TestCase

from . import views
from .provider import DraugiemProvider


class DraugiemTests(TestCase):
    def setUp(self):
        # workaround to create a session. see:
        # https://code.djangoproject.com/ticket/11475
        User.objects.create_user(
            "anakin", "skywalker@deathstar.example.com", "s1thrul3s"
        )
        self.client.login(username="anakin", password="s1thrul3s")

        app = SocialApp.objects.create(
            provider=DraugiemProvider.id,
            name=DraugiemProvider.id,
            client_id="app123id",
            key=DraugiemProvider.id,
            secret="dummy",
        )
        request = RequestFactory().get("/")
        self.provider = app.get_provider(request)
        if app_settings.SITES_ENABLED:
            from django.contrib.sites.models import Site

            app.sites.add(Site.objects.get_current())
        self.app = app

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
                    "img": "http://cdn.memegenerator.net/instances/500x/23395689.jpg",
                }
            },
        }

    def get_socialaccount(self, response, token):
        """
        Returns SocialLogin based on the data from the request
        """
        request = Mock()
        login = self.provider.sociallogin_from_response(request, response)
        login.token = token
        return login

    def mock_socialaccount_state(self):
        """
        SocialLogin depends on Session state - a tuple of request
        params and a random string
        """
        session = self.client.session
        session["socialaccount_state"] = (
            {"process": "login", "scope": "", "auth_params": ""},
            "12345",
        )
        session.save()

    def test_login_redirect(self):
        response = self.client.get(reverse(views.login))
        redirect_url = reverse(views.callback)
        full_redirect_url = "http://testserver" + redirect_url
        secret = self.app.secret + full_redirect_url
        redirect_url_hash = md5(secret.encode("utf-8")).hexdigest()
        params = {
            "app": self.app.client_id,
            "hash": redirect_url_hash,
            "redirect": full_redirect_url,
        }
        self.assertRedirects(
            response,
            "%s?%s" % (views.AUTHORIZE_URL, urlencode(params)),
            fetch_redirect_response=False,
        )

    def test_callback_no_auth_status(self):
        response = self.client.get(reverse(views.callback))
        self.assertTemplateUsed(response, "socialaccount/authentication_error.html")

    def test_callback_invalid_auth_status(self):
        response = self.client.get(reverse(views.callback), {"dr_auth_status": "fail"})
        self.assertTemplateUsed(response, "socialaccount/authentication_error.html")

    def test_callback(self):
        with patch(
            "allauth.socialaccount.providers.draugiem.views.draugiem_complete_login"
        ) as draugiem_complete_login:
            self.mock_socialaccount_state()

            response_json = self.get_draugiem_login_response()

            token = SocialToken(app=self.app, token=response_json["apikey"])
            login = self.get_socialaccount(response_json, token)

            draugiem_complete_login.return_value = login

            response = self.client.get(
                reverse(views.callback),
                {"dr_auth_status": "ok", "dr_auth_code": "42"},
            )
            self.assertRedirects(
                response, "/accounts/profile/", fetch_redirect_response=False
            )
            socialaccount = SocialAccount.objects.filter(
                provider=DraugiemProvider.id
            ).last()
            pacc = socialaccount.get_provider_account()
            assert (
                pacc.get_avatar_url()
                == "http://cdn.memegenerator.net/instances/500x/23395689.jpg"
            )
            assert pacc.to_str() == "Draugiem"
