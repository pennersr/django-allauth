from django.contrib.auth.models import User

from models import SocialAccount

class SocialAccountBackend:
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def authenticate(self, account=None):
        user = None
        if isinstance(account, SocialAccount):
            if account.pk:
                user = account.user
        return user
            

            
      
