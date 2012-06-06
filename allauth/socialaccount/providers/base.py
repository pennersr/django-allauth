class Provider(object):
    def wrap_account(self, social_account):
        return self.account_class(social_account)

class ProviderAccount(object):
    def __init__(self, social_account):
        self.account = social_account

    def get_profile_url(self):
        return None

    def get_avatar_url(self):
        return None

