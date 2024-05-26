from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import HttpResponseRedirect

from allauth import app_settings as allauth_settings
from allauth.account import app_settings as account_settings
from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.internal import flows
from allauth.account.models import EmailAddress
from allauth.core.exceptions import ReauthenticationRequired
from allauth.socialaccount import signals
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.models import SocialAccount, SocialLogin


def validate_disconnect(request, account):
    """
    Validate whether or not the socialaccount account can be
    safely disconnected.
    """
    accounts = SocialAccount.objects.filter(user_id=account.user_id)
    is_last = not accounts.exclude(pk=account.pk).exists()
    adapter = get_adapter()
    if is_last:
        if allauth_settings.SOCIALACCOUNT_ONLY:
            raise adapter.validation_error("disconnect_last")
        # No usable password would render the local account unusable
        if not account.user.has_usable_password():
            raise adapter.validation_error("no_password")
        # No email address, no password reset
        if (
            account_settings.EMAIL_VERIFICATION
            == account_settings.EmailVerificationMethod.MANDATORY
        ):
            if not EmailAddress.objects.filter(
                user=account.user, verified=True
            ).exists():
                raise adapter.validation_error("no_verified_email")
    adapter.validate_disconnect(account, accounts)


def disconnect(request, account):
    if account_settings.REAUTHENTICATION_REQUIRED:
        flows.reauthentication.raise_if_reauthentication_required(request)

    get_account_adapter().add_message(
        request,
        messages.INFO,
        "socialaccount/messages/account_disconnected.txt",
    )
    provider = account.get_provider()
    account.delete()
    signals.social_account_removed.send(
        sender=SocialAccount, request=request, socialaccount=account
    )
    get_adapter().send_notification_mail(
        "socialaccount/email/account_disconnected",
        request.user,
        context={
            "account": account,
            "provider": provider,
        },
    )


def resume_connect(request, serialized_state):
    sociallogin = SocialLogin.deserialize(serialized_state)
    return connect(request, sociallogin)


def connect(request, sociallogin):
    try:
        ok, action, message = do_connect(request, sociallogin)
    except PermissionDenied:
        # This should not happen. Simply redirect to the connections
        # view (which has a login required)
        connect_redirect_url = get_adapter().get_connect_redirect_url(
            request, sociallogin.account
        )
        return HttpResponseRedirect(connect_redirect_url)
    except ReauthenticationRequired:
        return flows.reauthentication.stash_and_reauthenticate(
            request,
            sociallogin.serialize(),
            "allauth.socialaccount.internal.flows.connect.resume_connect",
        )
    except ValidationError:
        ok, action, message = (
            False,
            None,
            "socialaccount/messages/account_connected_other.txt",
        )
    level = messages.INFO if ok else messages.ERROR
    default_next = get_adapter().get_connect_redirect_url(request, sociallogin.account)
    next_url = sociallogin.get_redirect_url(request) or default_next
    get_account_adapter(request).add_message(
        request,
        level,
        message,
        message_context={"sociallogin": sociallogin, "action": action},
    )
    return HttpResponseRedirect(next_url)


def do_connect(request, sociallogin):
    if request.user.is_anonymous:
        raise PermissionDenied()
    if account_settings.REAUTHENTICATION_REQUIRED:
        flows.reauthentication.raise_if_reauthentication_required(request)
    message = "socialaccount/messages/account_connected.txt"
    action = None
    ok = True
    if sociallogin.is_existing:
        if sociallogin.user != request.user:
            # Social account of other user. For now, this scenario
            # is not supported. Issue is that one cannot simply
            # remove the social account from the other user, as
            # that may render the account unusable.
            raise get_adapter().validation_error("connected_other")
        elif not sociallogin.account._state.adding:
            action = "updated"
            message = "socialaccount/messages/account_connected_updated.txt"
        else:
            action = "added"
            sociallogin.connect(request, request.user)
    else:
        # New account, let's connect
        action = "added"
        sociallogin.connect(request, request.user)
    return ok, action, message
