from django.contrib import messages


def logout(request):
    from allauth.account.adapter import get_adapter

    adapter = get_adapter()
    adapter.add_message(request, messages.SUCCESS, "account/messages/logged_out.txt")
    adapter.logout(request)
