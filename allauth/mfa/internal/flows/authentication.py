from allauth.account.authentication import record_authentication


def post_authentication(request, authenticator, reauthenticated=False):
    authenticator.record_usage()
    extra_data = {
        "id": authenticator.pk,
        "type": authenticator.type,
    }
    if reauthenticated:
        extra_data["reauthenticated"] = True
    record_authentication(request, "mfa", **extra_data)
