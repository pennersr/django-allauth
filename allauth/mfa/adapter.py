from allauth import app_settings as allauth_settings
from allauth.account.utils import user_email, user_username
from allauth.mfa import app_settings
from allauth.utils import import_attribute


class DefaultMFAAdapter:
    def __init__(self, request=None):
        self.request = request

    def get_totp_label(self, user):
        label = user_email(user)
        if not label:
            label = user_username(user)
        if not label:
            label = str(user)
        return label

    def get_totp_issuer(self):
        issuer = app_settings.TOTP_ISSUER
        if not issuer:
            if allauth_settings.SITES_ENABLED:
                from django.contrib.sites.models import Site

                issuer = Site.objects.get_current(self.request).name
            else:
                issuer = self.request.get_host()
        return issuer


def get_adapter(request=None):
    return import_attribute(app_settings.ADAPTER)(request)
