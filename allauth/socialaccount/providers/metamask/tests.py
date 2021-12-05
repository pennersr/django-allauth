from django.test.utils import override_settings
from django.urls import reverse

from allauth.tests import TestCase, patch
from allauth.utils import get_user_model
from .provider import MetamaskProvider

SOCIALACCOUNT_PROVIDERS = {"metamask": {"chainid": "6969"}}

class MetamaskTests(TestCase):
    @override_settings(SOCIALACCOUNT_PROVIDERS=SOCIALACCOUNT_PROVIDERS)
    provider_id = MetamaskProvider.id
