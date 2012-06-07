from emailconfirmation.models import EmailConfirmation
from emailconfirmation.signals import email_confirmed


def mark_user_active(sender, instance=None, **kwargs):
    user = kwargs.get("email_address").user
    user.is_active = True
    user.save()


email_confirmed.connect(mark_user_active, sender=EmailConfirmation)
