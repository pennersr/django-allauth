from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.http import urlencode

from allauth.socialaccount.providers.base import Provider, ProviderAccount


class TelegramAccount(ProviderAccount):
    pass


class TelegramProvider(Provider):
    id = "telegram"
    name = "Telegram"
    account_class = TelegramAccount
    supports_redirect = True

    def get_login_url(self, request, **kwargs):
        url = reverse("telegram_login")
        if kwargs:
            url = f"{url}?{urlencode(kwargs)}"
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

    def get_auth_date_validity(self):
        auth_date_validity = 30
        settings = self.get_settings()
        if "AUTH_PARAMS" in settings:
            auth_date_validity = settings.get("AUTH_PARAMS").get(
                "auth_date_validity", auth_date_validity
            )
        auth_date_validity = self.app.settings.get(
            "auth_date_validity", auth_date_validity
        )
        return auth_date_validity

    def redirect(self, request, process, next_url=None, data=None, **kwargs):
        state = self.stash_redirect_state(request, process, next_url, data, **kwargs)
        return_to = request.build_absolute_uri(
            f"{reverse('telegram_callback')}?{urlencode({'state': state})}"
        )
        url = "https://oauth.telegram.org/auth?" + urlencode(
            {
                "origin": request.build_absolute_uri("/"),
                "bot_id": self.app.client_id,
                "request_access": "write",
                "embed": "0",
                "return_to": return_to,
            }
        )
        return HttpResponseRedirect(url)


provider_classes = [TelegramProvider]
