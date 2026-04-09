from __future__ import annotations

from django.http import HttpRequest
from django.shortcuts import render

from allauth.account import app_settings as account_app_settings
from allauth.socialaccount import app_settings


def respond_to_login_on_get(request: HttpRequest, provider):
    if (not app_settings.LOGIN_ON_GET) and request.method == "GET":
        return render(
            request,
            f"socialaccount/login.{account_app_settings.TEMPLATE_EXTENSION}",
            {
                "provider": provider,
                "process": request.GET.get("process"),
            },
        )
