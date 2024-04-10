import time

from django.contrib import messages
from django.contrib.auth import get_user_model

from allauth.account import app_settings
from allauth.account.adapter import get_adapter
from allauth.account.internal.flows.login import (
    perform_login,
    send_unknown_account_email,
)
from allauth.account.models import Login


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
        send_unknown_account_email(request, email)
    else:
        user = users[0]
        code = adapter.generate_login_by_email_code()
        context = {
            "request": request,
            "code": code,
        }
        adapter.send_mail("account/email/login_by_email", email, context)
        pending_login.update({"code": code, "user_id": user.pk})

    request.session["account_login_by_email"] = pending_login
    adapter.add_message(
        request,
        messages.SUCCESS,
        "account/messages/login_by_email_code_sent.txt",
        {"email": email},
    )


def get_pending_login(request, peek=False):
    if peek:
        data = request.session.get("account_login_by_email")
    else:
        data = request.session.pop("account_login_by_email", None)
    if not data:
        return None, None
    if time.time() - data["at"] >= app_settings.LOGIN_BY_EMAIL_TIMEOUT:
        request.session.pop("account_login_by_email", None)
        return None, None
    user_id = data.get("user_id")
    user = None
    if user_id:
        user = get_user_model().objects.get(pk=user_id)
    return user, data


def record_invalid_attempt(request, pending_login):
    n = pending_login["failed_attempts"]
    n += 1
    pending_login["failed_attempts"] = n
    if n >= app_settings.LOGIN_BY_EMAIL_MAX_ATTEMPTS:
        request.session.pop("account_login_by_email", None)
        return False
    else:
        request.session["account_login_by_email"] = pending_login
        return True


def perform_login_by_email(request, user, redirect_url, pending_login):
    request.session.pop("account_login_by_email", None)
    login = Login(
        user=user,
        redirect_url=redirect_url,
        email=pending_login["email"],
    )
    return perform_login(request, login)
