from allauth.socialaccount.tests import OpenIDConnectTests
from allauth.tests import TestCase


class OpenIDConnectTests(OpenIDConnectTests, TestCase):
    provider_id = "oidc-server"


class OtherOpenIDConnectTests(OpenIDConnectTests, TestCase):
    provider_id = "other-oidc-server"
