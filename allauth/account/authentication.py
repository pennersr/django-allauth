from allauth.account.internal.flows.login import AUTHENTICATION_METHODS_SESSION_KEY


def get_authentication_records(request):
    return request.session.get(AUTHENTICATION_METHODS_SESSION_KEY, [])
