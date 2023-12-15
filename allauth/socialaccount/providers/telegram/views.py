import base64
import hashlib
import hmac
import json
import time

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.http import urlencode
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.helpers import (
    complete_social_login,
    render_authentication_error,
)

from .provider import TelegramProvider


class LoginView(View):
    def dispatch(self, request):
        provider = get_adapter().get_provider(request, TelegramProvider.id)
        return_to = request.build_absolute_uri(
            reverse("telegram_callback") + "?" + request.GET.urlencode()
        )

        url = "https://oauth.telegram.org/auth?" + urlencode(
            {
                "origin": request.build_absolute_uri("/"),
                "bot_id": provider.app.client_id,
                "request_access": "write",
                "embed": "0",
                "return_to": return_to,
            }
        )
        return HttpResponseRedirect(url)


login = LoginView.as_view()


@method_decorator(csrf_exempt, name="dispatch")
class CallbackView(View):
    def get(self, request):
        return render(request, "telegram/callback.html")

    def post(self, request):
        result = request.POST.get("tgAuthResult")
        padding = "=" * (4 - (len(result) % 4))
        data = json.loads(base64.b64decode(result + padding))
        adapter = get_adapter()
        provider = adapter.get_provider(request, TelegramProvider.id)
        hash = data.pop("hash")
        payload = "\n".join(sorted(["{}={}".format(k, v) for k, v in data.items()]))
        token = provider.app.secret
        token_sha256 = hashlib.sha256(token.encode()).digest()
        expected_hash = hmac.new(
            token_sha256, payload.encode(), hashlib.sha256
        ).hexdigest()
        auth_date = int(data.pop("auth_date"))
        auth_date_validity = provider.get_auth_date_validity()
        if hash != expected_hash or time.time() - auth_date > auth_date_validity:
            return render_authentication_error(
                request, provider=provider, extra_context={"response": data}
            )

        login = provider.sociallogin_from_response(request, data)
        process = request.GET.get("process")
        if process:
            login.state["process"] = process
        return complete_social_login(request, login)


callback = CallbackView.as_view()
