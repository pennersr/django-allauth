from allauth.account.authentication import record_authentication


def reauthenticate_by_password(request):
    record_authentication(request, method="password", reauthenticated=True)
