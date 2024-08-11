class AuthProcess:
    LOGIN = "login"
    CONNECT = "connect"
    REDIRECT = "redirect"


class AuthAction:
    AUTHENTICATE = "authenticate"
    REAUTHENTICATE = "reauthenticate"
    REREQUEST = "rerequest"


class AuthError:
    UNKNOWN = "unknown"
    CANCELLED = "cancelled"  # Cancelled on request of user
    DENIED = "denied"  # Denied by server
