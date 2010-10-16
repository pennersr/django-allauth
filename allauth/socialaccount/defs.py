class SocialAccountProvider:
    def __init__(self, id, name):
        self.id = id
        self.name = name
    
    def __str__(self):
        return self.id


SocialAccountProvider.TWITTER \
    = SocialAccountProvider(id="twitter", name="Twitter")
SocialAccountProvider.GOOGLE \
    = SocialAccountProvider(id='google', name='Google')
SocialAccountProvider.YAHOO \
    = SocialAccountProvider(id='yahoo', name='Yahoo')
SocialAccountProvider.HYVES \
    = SocialAccountProvider(id='hyves', name='Hyves')
SocialAccountProvider.OPENID \
    = SocialAccountProvider(id='openid', name='OpenID')
SocialAccountProvider.FACEBOOK \
    = SocialAccountProvider(id='facebook', name='Facebook')
