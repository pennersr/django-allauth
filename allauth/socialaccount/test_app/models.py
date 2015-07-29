from django.db import models
from allauth.socialaccount.models import SocialAppABC, SocialAppManager


class SocialAppSwapped(SocialAppABC):
    new_field = models.CharField(max_length=100)
