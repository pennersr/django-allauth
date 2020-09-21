from django.dispatch import Signal


# Sent after a user successfully authenticates via a social provider,
# but before the login is actually processed. This signal is emitted
# for social logins, signups and when connecting additional social
# accounts to an account.
# Provides the arguments "request", "sociallogin"
pre_social_login = Signal()

# Sent after a user connects a social account to a their local account.
# Provides the arguments "request", "sociallogin"
social_account_added = Signal()

# Sent after a user connects an already existing social account to a
# their local account. The social account will have an updated token and
# refreshed extra_data.
# Provides the arguments "request", "sociallogin"
social_account_updated = Signal()

# Sent after a user disconnects a social account from their local
# account.
# Provides the arguments "request", "socialaccount"
social_account_removed = Signal()
