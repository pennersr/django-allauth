from allauth.account.reauthentication import record_authentication


def reauthenticate(request):
    record_authentication(request, request.user)
