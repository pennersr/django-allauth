from django.db import models
from allauth.socialaccount.models import SocialAppABC, SocialAccountABC
import allauth


class SocialAppSwapped(SocialAppABC):
    new_field = models.CharField(max_length=100)

class SocialAccountSwapped(SocialAccountABC):
    new_field = models.CharField(max_length=100)
