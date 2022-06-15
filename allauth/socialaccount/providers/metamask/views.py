import json
import random
import string

from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from eth_account.messages import encode_defunct
# web3 declarations
from web3 import Web3

from allauth.socialaccount import providers
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.models import SocialLogin

from .provider import MetamaskProvider


@csrf_exempt
@require_http_methods(["POST"])
def nonce(request):
    extra_data = request.body.decode("utf-8")
    try:
        data = json.loads(extra_data)
    except ValueError as e:
        return JsonResponse(
            {"error": _("The value was not in JSON. error %s" % e), "success": False}
        )
    if ("account" not in data.keys()) or ("process" not in data.keys()):
        return JsonResponse({"error": _("JSON key error "), "success": False})
    nonce = "".join(
        random.SystemRandom().choice(string.ascii_uppercase + string.digits)
        for i in range(32)
    )
    request.session["metamask_state"] = {
        "account": data["account"],
        "nonce": nonce,
    }
    return JsonResponse({"data": nonce, "success": True}, safe=False)


@csrf_exempt
@require_http_methods(["POST"])
def verify(request):
    state = request.session.get("metamask_state")
    if not state:
        raise PermissionDenied()
    account = request.POST.get("account")
    if account != state["account"]:
        raise PermissionDenied()

    provider = providers.registry.by_id(MetamaskProvider.id, request)
    settings = provider.get_settings()
    w3 = Web3(Web3.HTTPProvider(settings["URL"]))

    message_hash = encode_defunct(text=state["nonce"])
    recoveredAddress = w3.eth.account.recover_message(
        message_hash, signature=request.POST.get("signature")
    )
    if recoveredAddress.lower() != account.lower():
        raise PermissionDenied()
    data = {
        "account": account.lower(),
    }
    login = provider.sociallogin_from_response(request, data)
    login.state = SocialLogin.state_from_request(request)
    return complete_social_login(request, login)
