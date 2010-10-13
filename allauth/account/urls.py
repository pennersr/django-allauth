from django.conf import settings
from django.conf.urls.defaults import *

from forms import SignupForm


import views

signup_view = "pinax.apps.signup_codes.views.signup"


urlpatterns = patterns("",
    url(r"^email/$", views.email, name="acct_email"),
    url(r"^signup/$", views.signup, name="acct_signup"),
    url(r"^login/$", views.login, name="acct_login"),
    url(r"^password_change/$", views.password_change, name="acct_passwd"),
    url(r"^password_set/$", views.password_set, name="acct_passwd_set"),
#    url(r"^password_delete/$", views.password_delete, name="acct_passwd_delete"),
#    url(r"^password_delete/done/$", "django.views.generic.simple.direct_to_template", {
#        "template": "account/password_delete_done.html",
#    }, name="acct_passwd_delete_done"),
    url(r"^logout/$", views.logout, name="acct_logout"),
    
    url(r"^confirm_email/(\w+)/$", "emailconfirmation.views.confirm_email", name="acct_confirm_email"),
    
    # password reset
    url(r"^password_reset/$", views.password_reset, name="acct_passwd_reset"),
    url(r"^password_reset/done/$", views.password_reset_done, name="acct_passwd_reset_done"),
    url(r"^password_reset_key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$", views.password_reset_from_key, name="acct_passwd_reset_key"),
    
)
