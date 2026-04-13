from django.dispatch import Signal


# Emitted after a user successfully authenticates via a social provider,
# but before the login is actually processed. This signal is emitted
# for social logins, signups and when connecting additional social
# accounts to an account.
# Arguments:
# - request: HttpRequest
# - sociallogin: SocialLogin
pre_social_login = Signal()

# Emitted after a user connects a social account to their local account.
# Arguments:
# - request: HttpRequest
# - sociallogin: SocialLogin
social_account_added = Signal()

# Emitted after a user connects an already existing social account to
# their local account. The social account will have an updated token and
# refreshed extra_data.
# Arguments:
# - request: HttpRequest
# - sociallogin: SocialLogin
social_account_updated = Signal()

# Emitted after a user disconnects a social account from their local
# account.
# Arguments:
# - request: HttpRequest
# - socialaccount: SocialAccount
social_account_removed = Signal()
