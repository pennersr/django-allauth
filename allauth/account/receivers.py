from datetime import datetime

from django.dispatch import receiver

from .adapter import get_adapter
from .signals import *


def send_password_change_notification(sender, request, user, **kwargs):
    adapter = get_adapter()
    template_prefix = "account/email/password_changed_notification"
    context = {
        "timestamp": datetime.now(),
        "username": user.username,
        "ip": adapter.get_client_ip(request),
        "browser_agent": adapter.get_browser_user_agent(request),
    }
    adapter.send_notification_mail(template_prefix, user, context)
