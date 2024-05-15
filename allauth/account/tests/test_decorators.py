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
