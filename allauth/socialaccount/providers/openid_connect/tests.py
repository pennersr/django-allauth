from allauth.socialaccount.tests import OpenIDConnectTests
from allauth.tests import TestCase


class OpenIDConnectTests(OpenIDConnectTests, TestCase):
    provider_id = "unittest-server"


class OtherOpenIDConnectTests(OpenIDConnectTests, TestCase):
    provider_id = "ther-server"
