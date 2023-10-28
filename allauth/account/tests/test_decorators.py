from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware

from pytest_django.asserts import assertTemplateUsed

from allauth.account.decorators import verified_email_required


def test_verified_email_required(user_factory, rf):
    user = user_factory(email_verified=False)

    @verified_email_required
    def view(request):
        assert False

    request = rf.get("/")
    SessionMiddleware(lambda request: None).process_request(request)
    MessageMiddleware(lambda request: None).process_request(request)
    request.user = user
    view(request)
    assertTemplateUsed("account/verified_email_required.html")
