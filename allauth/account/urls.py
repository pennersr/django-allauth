from django.conf.urls import patterns, url
from django.views.generic import RedirectView

from . import views

urlpatterns = patterns(
    "",
    url(r"^signup/$", views.signup, name="signup"),
    url(r"^login/$", views.login, name="login"),
    url(r"^logout/$", views.logout, name="logout"),

    url(r"^password/change/$", views.password_change,
        name="change_password"),
    url(r"^password/set/$", views.password_set, name="set_password"),

    url(r"^inactive/$", views.account_inactive, name="inactive"),

    # E-mail
    url(r"^email/$", views.email, name="email"),
    url(r"^confirm-email/$", views.email_verification_sent,
        name="email_verification_sent"),
    url(r"^confirm-email/(?P<key>\w+)/$", views.confirm_email,
        name="confirm_email"),
    # Handle old redirects
    url(r"^confirm_email/(?P<key>\w+)/$",
        RedirectView.as_view(url='/accounts/confirm-email/%(key)s/',
                             permanent=True)),

    # password reset
    url(r"^password/reset/$", views.password_reset,
        name="reset_password"),
    url(r"^password/reset/done/$", views.password_reset_done,
        name="reset_password_done"),
    url(r"^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$",
        views.password_reset_from_key,
        name="reset_password_from_key"),
    url(r"^password/reset/key/done/$", views.password_reset_from_key_done,
        name="reset_password_from_key_done"),
)
