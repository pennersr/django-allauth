from django.dispatch import Signal

# Sent after a user successfully authenticates via a social provider,
# but before the login is actually processed. This signal is emitted
# for social logins, signups and when connecting additional social
# accounts to an account.
pre_social_login = Signal(providing_args=["request", "sociallogin"])

# Sent after a user connects a social account to a their local account.
social_account_added = Signal(providing_args=["request", "sociallogin"])

# Sent after a user disconnects a social account from their local
# account.
social_account_removed = Signal(providing_args=["request", "socialaccount"])
