from allauth.socialaccount.providers.base import Provider, ProviderAccount


class TelegramAccount(ProviderAccount):
    pass


class TelegramProvider(Provider):
    id = "telegram"
    name = "Telegram"
    account_class = TelegramAccount

    def get_login_url(self, request, **kwargs):
        # TODO: Find a way to better wrap the iframed button
        return "#"

    def extract_uid(self, data):
        return data["id"]

    def extract_common_fields(self, data):
        return {
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "username": data["username"],
        }


provider_classes = [TelegramProvider]
