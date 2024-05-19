from django.http import HttpResponseRedirect
from django.urls import reverse

from allauth.account.authentication import record_authentication


STATE_SESSION_KEY = "account_reauthentication_state"


def reauthenticate_by_password(request):
    record_authentication(request, method="password", reauthenticated=True)


def stash_and_reauthenticate(request, state, callback):
    request.session[STATE_SESSION_KEY] = {
        "state": state,
        "callback": callback,
    }
    return HttpResponseRedirect(reverse("account_reauthenticate"))
