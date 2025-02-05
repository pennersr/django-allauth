from django.test import TestCase

from allauth.socialaccount.tests import OpenIDConnectTests


class MainOpenIDConnectTests(OpenIDConnectTests, TestCase):
    provider_id = "oidc-server"


class OtherOpenIDConnectTests(OpenIDConnectTests, TestCase):
    provider_id = "other-oidc-server"
