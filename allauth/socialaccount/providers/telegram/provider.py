from django.urls import reverse
from django.utils.http import urlencode

from allauth.socialaccount.providers.base import Provider, ProviderAccount


class TelegramAccount(ProviderAccount):
    pass


class TelegramProvider(Provider):
    id = "telegram"
    name = "Telegram"
    account_class = TelegramAccount

    def get_login_url(self, request, **kwargs):
        url = reverse("telegram_login")
        if kwargs:
            url = url + "?" + urlencode(kwargs)
        return url

    def extract_uid(self, data):
        return str(data["id"])

    def extract_common_fields(self, data):
        ret = {}
        if data.get("first_name"):
            ret["first_name"] = data.get("first_name")
        if data.get("last_name"):
            ret["last_name"] = data.get("last_name")
        if data.get("username"):
            ret["username"] = data.get("username")
        return ret


provider_classes = [TelegramProvider]
