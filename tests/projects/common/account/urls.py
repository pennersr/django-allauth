from django.urls import path

from tests.projects.common.account.views import check_verified_email


urlpatterns = [
    path(
        "check-verified-email/",
        check_verified_email,
        name="tests_account_check_verified_email",
    ),
]
