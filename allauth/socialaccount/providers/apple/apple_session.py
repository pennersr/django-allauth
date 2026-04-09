from django.http import HttpRequest

from allauth.socialaccount.sessions import LoginSession


APPLE_SESSION_COOKIE_NAME = "apple-login-session"


def get_apple_session(request: HttpRequest):
    return LoginSession(request, "apple_login_session", APPLE_SESSION_COOKIE_NAME)
