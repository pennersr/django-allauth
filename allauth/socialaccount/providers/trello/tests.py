from allauth.socialaccount.tests import OAuthTestsMixin
from allauth.tests import TestCase

from .provider import TrelloProvider


class TrelloTests(OAuthTestsMixin, TestCase):
    provider_id = TrelloProvider.id
