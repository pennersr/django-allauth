import time

from django.contrib import messages
from django.contrib.auth import get_user_model

from allauth.account import app_settings
from allauth.account.adapter import get_adapter
from allauth.account.authentication import record_authentication
from allauth.account.internal.flows.login import perform_login
from allauth.account.internal.flows.signup import send_unknown_account_mail
from allauth.account.models import Login


LOGIN_CODE_SESSION_KEY = "account_login_code"


def request_login_code(request, email):
    from allauth.account.utils import filter_users_by_email

    adapter = get_adapter()
    users = filter_users_by_email(email, is_active=True, prefer_verified=True)
    pending_login = {
        "at": time.time(),
        "email": email,
        "failed_attempts": 0,
    }
    if not users:
        send_unknown_account_mail(request, email)
    else:
        user = users[0]
        code = adapter.generate_login_code()
        context = {
            "request": request,
            "code": code,
        }
        adapter.send_mail("account/email/login_code", email, context)
        pending_login.update(
            {"code": code, "user_id": user._meta.pk.value_to_string(user)}
        )

    request.session[LOGIN_CODE_SESSION_KEY] = pending_login
    adapter.add_message(
        request,
        messages.SUCCESS,
        "account/messages/login_code_sent.txt",
        {"email": email},
    )


def get_pending_login(request, peek=False):
    if peek:
        data = request.session.get(LOGIN_CODE_SESSION_KEY)
    else:
        data = request.session.pop(LOGIN_CODE_SESSION_KEY, None)
    if not data:
        return None, None
    if time.time() - data["at"] >= app_settings.LOGIN_BY_CODE_TIMEOUT:
        request.session.pop(LOGIN_CODE_SESSION_KEY, None)
        return None, None
    user_id_str = data.get("user_id")
    user = None
    if user_id_str:
        user_id = get_user_model()._meta.pk.to_python(user_id_str)
        user = get_user_model().objects.get(pk=user_id)
    return user, data


def record_invalid_attempt(request, pending_login):
    n = pending_login["failed_attempts"]
    n += 1
    pending_login["failed_attempts"] = n
    if n >= app_settings.LOGIN_BY_CODE_MAX_ATTEMPTS:
        request.session.pop(LOGIN_CODE_SESSION_KEY, None)
        return False
    else:
        request.session[LOGIN_CODE_SESSION_KEY] = pending_login
        return True


def perform_login_by_code(request, user, redirect_url, pending_login):
    request.session.pop(LOGIN_CODE_SESSION_KEY, None)
    record_authentication(request, method="code", email=pending_login["email"])
    login = Login(
        user=user,
        redirect_url=redirect_url,
        email=pending_login["email"],
    )
    return perform_login(request, login)
