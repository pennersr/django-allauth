import time


AUTHENTICATION_METHODS_SESSION_KEY = "account_authentication_methods"


def record_authentication(request, method, **extra_data):
    """Here we keep a log of all authentication methods used within the current
    session.  Important to note is that having entries here does not imply that
    a user is fully signed in. For example, consider a case where a user
    authenticates using a password, but fails to complete the 2FA challenge.
    Or, a user successfully signs in into an inactive account or one that still
    needs verification. In such cases, ``request.user`` is still anonymous, yet,
    we do have an entry here.

    Example data::

        {'method': 'password',
         'at': 1701423602.7184925,
         'username': 'john.doe'}

        {'method': 'socialaccount',
         'at': 1701423567.6368647,
         'provider': 'amazon',
         'uid': 'amzn1.account.K2LI23KL2LK2'}

        {'method': 'mfa',
         'at': 1701423602.6392953,
         'id': 1,
         'type': 'totp'}

    """
    methods = request.session.get(AUTHENTICATION_METHODS_SESSION_KEY, [])
    data = {
        "method": method,
        "at": time.time(),
        **extra_data,
    }
    methods.append(data)
    request.session[AUTHENTICATION_METHODS_SESSION_KEY] = methods


def get_authentication_records(request):
    return request.session.get(AUTHENTICATION_METHODS_SESSION_KEY, [])
