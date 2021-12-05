from __future__ import unicode_literals

from allauth.socialaccount.tests import OAuthTestsMixin
from allauth.tests import TestCase

from .provider import MetamaskProvider


class MetamaskTests(OAuthTestsMixin, TestCase):
    provider_id = MetamaskProvider.id
