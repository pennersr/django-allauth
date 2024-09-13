import base64
import binascii
import hashlib
import hmac
import json
import time

from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from allauth.account.internal.decorators import login_not_required
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.helpers import (
    complete_social_login,
    render_authentication_error,
)
from allauth.socialaccount.providers.base.views import BaseLoginView
from allauth.socialaccount.providers.telegram.provider import TelegramProvider


@method_decorator(login_not_required, name="dispatch")
class LoginView(BaseLoginView):
    provider_id = TelegramProvider.id


login = LoginView.as_view()


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(login_not_required, name="dispatch")
class CallbackView(View):
    def get(self, request):
        return render(request, "telegram/callback.html")

    def post(self, request):
        adapter = get_adapter()
        provider = adapter.get_provider(request, TelegramProvider.id)

        state_id = request.GET.get("state")
        if not state_id:
            return render_authentication_error(
                request,
                provider=provider,
            )

        try:
            result = request.POST.get("tgAuthResult")
            padding = "=" * (4 - (len(result) % 4))
            data = json.loads(base64.b64decode(result + padding))
            if not isinstance(data, dict) or "hash" not in data:
                raise ValueError("Invalid tgAuthResult")
        except (binascii.Error, json.JSONDecodeError, ValueError) as e:
            return render_authentication_error(
                request,
                provider=provider,
                exception=e,
                extra_context={"state_id": state_id},
            )
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
                request,
                provider=provider,
                extra_context={"response": data, "state_id": state_id},
            )
        login = provider.sociallogin_from_response(request, data)
        login.state = provider.unstash_redirect_state(request, state_id)
        return complete_social_login(request, login)


callback = CallbackView.as_view()
