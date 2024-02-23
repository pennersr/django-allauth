from urllib.parse import quote

from allauth.account.adapter import DefaultAccountAdapter


class AccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):
        """
        Returns a frontend URL
        """
        return self.request.build_absolute_uri(
            f"/account/verify-email/{quote(emailconfirmation.key)}"
        )

    def get_reset_password_from_key_url(self, key):
        """
        Returns a frontend URL
        """
        return self.request.build_absolute_uri(f"/account/password/reset/key/{quote(key)}")
