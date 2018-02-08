from allauth.socialaccount.providers.base import Provider, ProviderAccount


class TelegramAccount(ProviderAccount):
    pass


class TelegramProvider(Provider):
    id = 'telegram'
    name = 'Telegram'
    account_class = TelegramAccount

    def get_login_url(self, request, **kwargs):
        # TODO: Find a way to better wrap the iframed button
        return '#'

    def extract_uid(self, data):
        return data['id']


provider_classes = [TelegramProvider]
