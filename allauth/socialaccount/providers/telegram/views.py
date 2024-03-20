import base64
import hashlib
import hmac
import json
import time

from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.helpers import (
    complete_social_login,
    render_authentication_error,
)
from allauth.socialaccount.models import SocialLogin
from allauth.socialaccount.providers.base.utils import respond_to_login_on_get
from allauth.socialaccount.providers.telegram.provider import TelegramProvider


class LoginView(View):
    def dispatch(self, request):
        provider = get_adapter().get_provider(request, TelegramProvider.id)
        resp = respond_to_login_on_get(request, provider)
        if resp:
            return resp
        return provider.redirect_from_request(request)


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
        state = request.GET.get("state")
        if not state:
            return render_authentication_error(
                request,
                provider=provider,
            )
        login = provider.sociallogin_from_response(request, data)
        login.state = SocialLogin.verify_and_unstash_state(request, state)
        return complete_social_login(request, login)


callback = CallbackView.as_view()
