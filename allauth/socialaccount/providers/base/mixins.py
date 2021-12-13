from django.shortcuts import render

from allauth.socialaccount import app_settings


class OAuthLoginMixin:
    def dispatch(self, request, *args, **kwargs):
        provider = self.adapter.get_provider()
        if (not app_settings.LOGIN_ON_GET) and request.method == "GET":
            return render(
                request,
                "socialaccount/login.html",
                {
                    "provider": provider,
                    "process": request.GET.get("process"),
                },
            )
        return self.login(request, *args, **kwargs)

    def login(self, request, *args, **kwargs):
        raise NotImplementedError
