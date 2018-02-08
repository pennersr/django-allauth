import hashlib
import hmac
import time

from allauth.socialaccount import providers
from allauth.socialaccount.helpers import (
    complete_social_login,
    render_authentication_error,
)

from .provider import TelegramProvider


def telegram_login(request):
    provider = providers.registry.by_id(TelegramProvider.id, request)
    data = dict(request.GET.items())
    hash = data.pop('hash')
    payload = '\n'.join(sorted([
        '{}={}'.format(k, v)
        for k, v in data.items()
    ]))
    token = provider.get_settings()['TOKEN']
    token_sha256 = hashlib.sha256(token.encode()).digest()
    expected_hash = hmac.new(
        token_sha256,
        payload.encode(),
        hashlib.sha256).hexdigest()
    auth_date = int(data.pop('auth_date'))
    if hash != expected_hash or time.time() - auth_date > 30:
        return render_authentication_error(
            request,
            provider_id=provider.id,
            extra_context={'response': data})

    login = provider.sociallogin_from_response(request, data)
    return complete_social_login(request, login)
