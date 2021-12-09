from allauth.socialaccount.providers.metamask.provider import MetamaskProvider
from django.test.utils import override_settings
from django.urls import reverse

from allauth.tests import TestCase, patch
from allauth.utils import get_user_model


SOCIALACCOUNT_PROVIDERS = {
    'metamask': {
        # For each OAuth based provider, either add a ``SocialApp``
        # (``socialaccount`` app) containing the required client
        # credentials, or list them here:
        'PRIMARY': {
            'CHAIN_ID': '6969',
            'URL': 'https://cloudflare-eth.com/',
            'PORT': '80'
        }
    }
}

class MetamaskTests(TestCase):
    provider_id = MetamaskProvider.id
