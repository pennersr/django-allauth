from django.urls import reverse

from pytest_django.asserts import assertTemplateUsed

from allauth.account.decorators import verified_email_required


def test_verified_email_required(user_factory, request_factory):
    user = user_factory(email_verified=False)

    @verified_email_required
    def view(request):
        assert False

    request = request_factory.get("/")
    request.user = user
    view(request)
    assertTemplateUsed("account/verified_email_required.html")


def test_secure_admin_login_skips_admin_login_next(client):
    """
    Test that we're not using 'next=/admin/login%2Fnext=/foo'
    """
    resp = client.get(reverse("admin:login") + "?next=/foo")
    assert resp["location"] == "/login/?next=%2Ffoo"


def test_secure_admin_login_denies_regular_users(auth_client):
    resp = auth_client.get(reverse("admin:login"))
    assert resp.status_code == 403


def test_secure_admin_login_passes_staff(auth_client, user):
    user.is_staff = True
    user.is_superuser = True
    user.save(update_fields=["is_staff", "is_superuser"])
    resp = auth_client.get(reverse("admin:auth_user_changelist"))
    assert resp.status_code == 200
