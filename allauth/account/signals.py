from django.dispatch import Signal

user_logged_in = Signal(providing_args=["request", "user"])

# Typically followed by `user_logged_in` (unless, e-mail verification kicks in)
user_signed_up = Signal(providing_args=["request", "user"])

password_set = Signal(providing_args=["request", "user"])
password_changed = Signal(providing_args=["request", "user"])
password_reset = Signal(providing_args=["request", "user"])

email_confirmed = Signal(providing_args=["request", "email_address"])
email_confirmation_sent = Signal(
    providing_args=["request", "confirmation", "signup"])

email_changed = Signal(
    providing_args=[
        "request", "user",
        "from_email_address", "to_email_address"])
email_added = Signal(providing_args=["request", "user", "email_address"])
email_removed = Signal(providing_args=["request", "user", "email_address"])
