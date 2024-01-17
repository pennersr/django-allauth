from datetime import timedelta
from unittest.mock import Mock, patch

from django.conf import settings
from django.contrib.auth import SESSION_KEY, get_user_model
from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.timezone import now

from pytest_django.asserts import (
    assertRedirects,
    assertTemplateNotUsed,
    assertTemplateUsed,
)

from allauth.account import app_settings
from allauth.account.models import (
    EmailAddress,
    EmailConfirmation,
    EmailConfirmationHMAC,
)
from allauth.account.signals import user_logged_in
from allauth.account.utils import user_pk_to_url_str

from .test_models import UUIDUser


def test_login_on_confirm(user_factory, client):
    settings.ACCOUNT_EMAIL_CONFIRMATION_HMAC = True
    settings.ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
    user = user_factory(email_verified=False)
    email = EmailAddress.objects.get_for_user(user, user.email)
    key = EmailConfirmationHMAC(email).key

    receiver_mock = Mock()  # we've logged if signal was called
    user_logged_in.connect(receiver_mock)

    # fake post-signup account_user stash
    session = client.session
    session["account_user"] = user_pk_to_url_str(user)
    session.save()

    resp = client.post(reverse("account_confirm_email", args=[key]))
    email = EmailAddress.objects.get(pk=email.pk)
    assert email.verified

    receiver_mock.assert_called_once_with(
        sender=get_user_model(),
        request=resp.wsgi_request,
        response=resp,
        user=user,
        signal=user_logged_in,
    )

    user_logged_in.disconnect(receiver_mock)


@patch("allauth.account.views.perform_login")
@patch("allauth.account.utils.get_user_model", return_value=UUIDUser)
def test_login_on_confirm_uuid_user(
    mocked_gum, mock_perform_login, settings, client, db
):
    settings.ACCOUNT_EMAIL_CONFIRMATION_HMAC = True
    settings.ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True

    user = UUIDUser(is_active=True, email="john@example.com", username="john")

    # fake post-signup account_user stash
    session = client.session
    session["account_user"] = user_pk_to_url_str(user)
    session.save()

    # fake email and email confirmation to avoid swappable model hell
    email = Mock(verified=False, user=user)
    key = "mockkey"
    confirmation = Mock(autospec=EmailConfirmationHMAC, key=key)
    confirmation.email_address = email
    confirmation.from_key.return_value = confirmation
    mock_perform_login.return_value = HttpResponseRedirect(redirect_to="/")

    with patch("allauth.account.views.EmailConfirmationHMAC", confirmation):
        client.post(reverse("account_confirm_email", args=[key]))

    assert mock_perform_login.called


def test_email_verification_failed(settings, user_factory, client):
    settings.ACCOUNT_EMAIL_CONFIRMATION_HMAC = (False,)
    user_factory(email_verified=True, email="foo@bar.org")
    unverified_user = user_factory(email_verified=False, email="foo@bar.org")
    email_address = EmailAddress.objects.get_for_user(
        unverified_user, unverified_user.email
    )
    assert not email_address.verified
    confirmation = EmailConfirmation.objects.create(
        email_address=email_address,
        key="dummy",
        sent=now(),
    )
    resp = client.post(reverse("account_confirm_email", args=[confirmation.key]))
    assertTemplateUsed(resp, "account/messages/email_confirmation_failed.txt")


def test_email_verification_mandatory(settings, db, client, mailoutbox, enable_cache):
    settings.ACCOUNT_EMAIL_CONFIRMATION_HMAC = False
    settings.ACCOUNT_EMAIL_CONFIRMATION_COOLDOWN = 10
    settings.ACCOUNT_EMAIL_VERIFICATION = app_settings.EmailVerificationMethod.MANDATORY
    # Signup
    resp = client.post(
        reverse("account_signup"),
        {
            "username": "johndoe",
            "email": "john@example.com",
            "password1": "johndoe",
            "password2": "johndoe",
        },
        follow=True,
    )
    assert resp.status_code == 200
    assert mailoutbox[0].to == ["john@example.com"]
    assert mailoutbox[0].body.find("http://") > 0
    assert len(mailoutbox) == 1
    assertTemplateUsed(
        resp,
        "account/verification_sent.%s" % app_settings.TEMPLATE_EXTENSION,
    )
    # Attempt to login, unverified
    for attempt in [1, 2]:
        resp = client.post(
            reverse("account_login"),
            {"login": "johndoe", "password": "johndoe"},
            follow=True,
        )
        # is_active is controlled by the admin to manually disable
        # users. I don't want this flag to flip automatically whenever
        # users verify their email addresses.
        assert (
            get_user_model().objects.filter(username="johndoe", is_active=True).exists()
        )

        assertTemplateUsed(
            resp,
            "account/verification_sent." + app_settings.TEMPLATE_EXTENSION,
        )
        # Attempt 1: no mail is sent due to cool-down ,
        # but there was already a mail in the outbox.
        assert len(mailoutbox) == attempt
        assert (
            EmailConfirmation.objects.filter(
                email_address__email="john@example.com"
            ).count()
            == attempt
        )
        # Wait for cooldown -- wipe cache (incl. rate limits)
        cache.clear()
    # Verify, and re-attempt to login.
    confirmation = EmailConfirmation.objects.filter(
        email_address__user__username="johndoe"
    )[:1].get()
    resp = client.get(reverse("account_confirm_email", args=[confirmation.key]))
    assertTemplateUsed(
        resp, "account/email_confirm.%s" % app_settings.TEMPLATE_EXTENSION
    )
    client.post(reverse("account_confirm_email", args=[confirmation.key]))
    resp = client.post(
        reverse("account_login"),
        {"login": "johndoe", "password": "johndoe"},
    )
    assertRedirects(resp, settings.LOGIN_REDIRECT_URL, fetch_redirect_response=False)


def test_optional_email_verification(settings, client, db, mailoutbox):
    settings.ACCOUNT_SIGNUP_REDIRECT_URL = "/accounts/welcome/"
    settings.ACCOUNT_EMAIL_VERIFICATION = app_settings.EmailVerificationMethod.OPTIONAL
    settings.ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False
    # Signup
    client.get(reverse("account_signup"))
    resp = client.post(
        reverse("account_signup"),
        {
            "username": "johndoe",
            "email": "john@example.com",
            "password1": "johndoe",
        },
    )
    # Logged in
    assertRedirects(
        resp, settings.ACCOUNT_SIGNUP_REDIRECT_URL, fetch_redirect_response=False
    )
    assert mailoutbox[0].to == ["john@example.com"]
    assert len(mailoutbox) == 1
    # Logout & login again
    client.logout()
    # Wait for cooldown
    EmailConfirmation.objects.update(sent=now() - timedelta(days=1))
    # Signup
    resp = client.post(
        reverse("account_login"),
        {"login": "johndoe", "password": "johndoe"},
    )
    assertRedirects(resp, settings.LOGIN_REDIRECT_URL, fetch_redirect_response=False)
    assert mailoutbox[0].to == ["john@example.com"]
    # There was an issue that we sent out email confirmation mails
    # on each login in case of optional verification. Make sure
    # this is not the case:
    assert len(mailoutbox) == 1


def test_email_confirmation_hmac_falls_back(user_factory, client):
    settings.ACCOUNT_EMAIL_CONFIRMATION_HMAC = True
    user = user_factory(email_verified=False)
    email = EmailAddress.objects.get_for_user(user, user.email)
    confirmation = EmailConfirmation.create(email)
    confirmation.sent = now()
    confirmation.save()
    client.post(reverse("account_confirm_email", args=[confirmation.key]))
    email = EmailAddress.objects.get(pk=email.pk)
    assert email.verified


def test_email_confirmation_hmac(settings, client, user_factory, mailoutbox, rf):
    settings.ACCOUNT_EMAIL_CONFIRMATION_HMAC = True
    user = user_factory(email_verified=False)
    email = EmailAddress.objects.get_for_user(user, user.email)
    confirmation = EmailConfirmationHMAC(email)
    request = rf.get("/")
    confirmation.send(request=request)
    assert len(mailoutbox) == 1
    client.post(reverse("account_confirm_email", args=[confirmation.key]))
    email = EmailAddress.objects.get(pk=email.pk)
    assert email.verified


def test_email_confirmation_hmac_timeout(
    settings, user_factory, client, mailoutbox, rf
):
    settings.ACCOUNT_EMAIL_CONFIRMATION_HMAC = True
    settings.ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 0
    user = user_factory(email_verified=False)
    email = EmailAddress.objects.get_for_user(user, user.email)
    confirmation = EmailConfirmationHMAC(email)
    request = rf.get("/")
    confirmation.send(request=request)
    assert len(mailoutbox) == 1
    client.post(reverse("account_confirm_email", args=[confirmation.key]))
    email = EmailAddress.objects.get(pk=email.pk)
    assert not email.verified


def test_confirm_email_with_another_user_logged_in(
    settings, user_factory, client, mailoutbox
):
    """Test the email confirmation view. If User B clicks on an email
    verification link while logged in as User A, ensure User A gets
    logged out."""
    settings.ACCOUNT_AUTHENTICATION_METHOD = app_settings.AuthenticationMethod.EMAIL
    user = user_factory(email_verified=False)
    client.force_login(user)
    client.post(reverse("account_email"), {"email": user.email, "action_send": ""})
    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == [user.email]
    client.logout()

    body = mailoutbox[0].body
    assert body.find("http://") > 0

    user2 = user_factory(email_verified=False, password="doe")
    resp = client.post(
        reverse("account_login"),
        {
            "login": user2.email,
            "password": "doe",
        },
    )
    assert user2 == resp.context["user"]

    url = body[body.find("/confirm-email/") :].split()[0]
    resp = client.post(url)

    assertTemplateUsed(resp, "account/messages/logged_out.txt")
    assertTemplateUsed(resp, "account/messages/email_confirmed.txt")

    assertRedirects(resp, settings.LOGIN_URL, fetch_redirect_response=False)


def test_confirm_email_with_same_user_logged_in(
    settings, user_factory, client, mailoutbox
):
    """If the user clicks on an email verification link while logged in, ensure
    the user stays logged in.
    """
    settings.ACCOUNT_AUTHENTICATION_METHOD = app_settings.AuthenticationMethod.EMAIL
    user = user_factory(email_verified=False)
    client.force_login(user)
    client.post(reverse("account_email"), {"email": user.email, "action_send": ""})
    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == [user.email]

    body = mailoutbox[0].body
    assert body.find("http://") > 0

    url = body[body.find("/confirm-email/") :].split()[0]
    resp = client.post(url)

    assertTemplateNotUsed(resp, "account/messages/logged_out.txt")
    assertTemplateUsed(resp, "account/messages/email_confirmed.txt")

    assertRedirects(resp, settings.LOGIN_REDIRECT_URL, fetch_redirect_response=False)

    assert user == resp.wsgi_request.user


def test_confirm_logs_out_user(auth_client, settings, user, user_factory):
    """
    When a user is signed in, and you follow an email confirmation link of
    another user within the same browser/session, be sure to sign out the signed
    in user.
    """
    settings.ACCOUNT_CONFIRM_EMAIL_ON_GET = False
    confirming_user = user_factory(email_verified=False)
    assert auth_client.session[SESSION_KEY] == str(user.pk)
    email = EmailAddress.objects.get(user=confirming_user, verified=False)
    auth_client.get(
        reverse(
            "account_confirm_email", kwargs={"key": EmailConfirmationHMAC(email).key}
        )
    )
    assert not auth_client.session.get(SESSION_KEY)
