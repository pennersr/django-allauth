from django.contrib import messages
from django.http import HttpRequest


def logout(request: HttpRequest) -> None:
    from allauth.account.adapter import get_adapter

    adapter = get_adapter()
    adapter.add_message(request, messages.SUCCESS, "account/messages/logged_out.txt")
    adapter.logout(request)
