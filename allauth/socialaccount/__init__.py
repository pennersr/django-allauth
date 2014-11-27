
#Ok, this is really weird but, in python3.2 we must import app_settings before
# django imports apps; otherwise the module-class hack doesn't work as expected
from . import app_settings

default_app_config = 'allauth.socialaccount.apps.SocialAccountConfig'
