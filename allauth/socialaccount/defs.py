class Provider:
    def __init__(self, id, name):
        self.id = id
        self.name = name
    
    def __str__(self):
        return self.id


Provider.TWITTER \
    = Provider(id="twitter", name="Twitter")
Provider.GOOGLE \
    = Provider(id='google', name='Google')
Provider.YAHOO \
    = Provider(id='yahoo', name='Yahoo')
Provider.HYVES \
    = Provider(id='hyves', name='Hyves')
Provider.OPENID \
    = Provider(id='openid', name='OpenID')
Provider.FACEBOOK \
    = Provider(id='facebook', name='Facebook')
Provider.LINKEDIN \
    = Provider(id='linkedin', name='LinkedIn')


PROVIDER_CHOICES = ((Provider.TWITTER.id, Provider.TWITTER.name),
                    (Provider.FACEBOOK.id, Provider.FACEBOOK.name),
                    (Provider.OPENID.id, Provider.OPENID.name),
                    (Provider.LINKEDIN.id, Provider.LINKEDIN.name))

# Legacy -- to be removed
SocialAccountProvider = Provider
