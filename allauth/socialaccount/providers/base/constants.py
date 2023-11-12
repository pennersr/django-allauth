class AuthProcess(object):
    LOGIN = "login"
    CONNECT = "connect"
    REDIRECT = "redirect"


class AuthAction(object):
    AUTHENTICATE = "authenticate"
    REAUTHENTICATE = "reauthenticate"
    REREQUEST = "rerequest"


class AuthError(object):
    UNKNOWN = "unknown"
    CANCELLED = "cancelled"  # Cancelled on request of user
    DENIED = "denied"  # Denied by server
