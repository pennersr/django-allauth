from django.contrib.auth.signals import user_logged_out  # noqa
from django.dispatch import Signal


# Provides the arguments "request", "user"
user_logged_in = Signal()

# Typically followed by `user_logged_in` (unless, e-mail verification kicks in)
# Provides the arguments "request", "user"
user_signed_up = Signal()

# Provides the arguments "request", "user"
password_set = Signal()
# Provides the arguments "request", "user"
password_changed = Signal()
# Provides the arguments "request", "user"
password_reset = Signal()

# Provides the arguments "request", "email_address"
email_confirmed = Signal()
# Provides the arguments "request", "confirmation", "signup"
email_confirmation_sent = Signal()

# Provides the arguments "request", "user", "from_email_address",
# "to_email_address"
email_changed = Signal()
# Provides the arguments "request", "user", "email_address"
email_added = Signal()
# Provides the arguments "request", "user", "email_address"
email_removed = Signal()
