from allauth.socialaccount.providers.base.utils import respond_to_login_on_get


class OAuthLoginMixin:
    def dispatch(self, request, *args, **kwargs):
        provider = self.adapter.get_provider()
        resp = respond_to_login_on_get(request, provider)
        if resp:
            return resp
        return self.login(request, *args, **kwargs)

    def login(self, request, *args, **kwargs):
        raise NotImplementedError
