from django.test.utils import override_settings

from allauth.socialaccount.models import SocialAccount
from allauth.tests import TestCase
from allauth.utils import get_user_model


class UtilTests(TestCase):
    def test_social_account_str_default(self):
        User = get_user_model()
        user = User(username="test")
        sa = SocialAccount(user=user)
        self.assertEqual("test", str(sa))

    def socialaccount_str_custom_formatter(socialaccount):
        return "A custom str builder for {}".format(socialaccount.user)

    @override_settings(
        SOCIALACCOUNT_SOCIALACCOUNT_STR=socialaccount_str_custom_formatter
    )
    def test_social_account_str_customized(self):
        User = get_user_model()
        user = User(username="test")
        sa = SocialAccount(user=user)
        self.assertEqual("A custom str builder for test", str(sa))
