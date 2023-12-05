from .models import UserSession


def on_user_logged_in(sender, **kwargs):
    request = kwargs["request"]
    UserSession.objects.create_from_request(request)
