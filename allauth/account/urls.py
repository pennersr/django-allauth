from django.conf.urls import patterns, url
from django.views.generic import RedirectView

from . import views, app_settings

urlpatterns = patterns(
    "",
    url(r"^signup/$", views.signup, name="account_signup"),
    url(r"^login/$", views.login, name="account_login"),
    url(r"^logout/$", views.logout, name="account_logout"),

    url(r"^password/change/$", views.password_change,
        name="account_change_password"),
    url(r"^password/set/$", views.password_set, name="account_set_password"),

    url(r"^inactive/$", views.account_inactive, name="account_inactive"),

    # E-mail
    url(r"^email/$", views.email, name="account_email"),
    url(r"^confirm-email/$", views.email_verification_sent,
        name="account_email_verification_sent"),
    url(r"^confirm-email/(?P<key>\w+)/$", views.confirm_email,
        name="account_confirm_email"),
    # Handle old redirects
    url(r"^confirm_email/(?P<key>\w+)/$",
        RedirectView.as_view(url='/accounts/confirm-email/%(key)s/',
                             permanent=True)),

    # password reset
    url(r"^password/reset/$", views.password_reset,
        name="account_reset_password"),
    url(r"^password/reset/done/$", views.password_reset_done,
        name="account_reset_password_done"),
    url(r"^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$",
        views.password_reset_from_key,
        name="account_reset_password_from_key"),
    url(r"^password/reset/key/done/$", views.password_reset_from_key_done,
        name="account_reset_password_from_key_done"),


)

if app_settings.TWO_FACTOR_ENABLED:
    urlpatterns = patterns('',
        url(r"^two_factor/setup$", views.two_factor_setup,
            name="two-factor-setup"),
        url(r"^two_factor/backup_tokens$", views.two_factor_backup_tokens,
            name="two-factor-backup-tokens"),
        url(r"^two_factor/qr_code$", views.two_factor_qr_code_generator,
            name="two-factor-qr-code"),
    )
