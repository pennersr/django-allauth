from django.test import RequestFactory, TestCase
from django.utils.http import base36_to_int, int_to_base36
from django.views import csrf

from allauth import app_settings, utils


class BasicTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_generate_unique_username(self):
        examples = [
            ("a.b-c@example.com", "a.b-c"),
            ("Üsêrnamê", "username"),
            ("User Name", "user_name"),
            ("", "user"),
        ]
        for input, username in examples:
            self.assertEqual(utils.generate_unique_username([input]), username)

    def test_email_validation(self):
        s = "this.email.address.is.a.bit.too.long.but.should.still.validate@example.com"  # noqa
        self.assertEqual(s, utils.valid_email_or_none(s))

    def test_build_absolute_uri(self):
        request = None
        if not app_settings.SITES_ENABLED:
            request = self.factory.get("/")
            request.META["SERVER_NAME"] = "example.com"
        self.assertEqual(
            utils.build_absolute_uri(request, "/foo"), "http://example.com/foo"
        )
        self.assertEqual(
            utils.build_absolute_uri(request, "/foo", protocol="ftp"),
            "ftp://example.com/foo",
        )
        self.assertEqual(
            utils.build_absolute_uri(request, "http://foo.com/bar"),
            "http://foo.com/bar",
        )

    def test_int_to_base36(self):
        n = 55798679658823689999
        b36 = "brxk553wvxbf3"
        assert int_to_base36(n) == b36
        assert base36_to_int(b36) == n

    def test_templatetag_with_csrf_failure(self):
        # Generate a fictitious GET request
        from allauth.socialaccount.models import SocialApp

        app = SocialApp.objects.create(provider="google")
        if app_settings.SITES_ENABLED:
            from django.contrib.sites.models import Site

            app.sites.add(Site.objects.get_current())

        request = self.factory.get("/tests/test_403_csrf.html")
        # Simulate a CSRF failure by calling the View directly
        # This template is using the `provider_login_url` templatetag
        response = csrf.csrf_failure(request, template_name="tests/test_403_csrf.html")
        # Ensure that CSRF failures with this template
        # tag succeed with the expected 403 response
        self.assertEqual(response.status_code, 403)
