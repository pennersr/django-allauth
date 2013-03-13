from allauth.socialaccount.models import SocialApp, SocialAccount, SocialToken
from django.utils.timezone import make_aware, utc
from anonymizer import Anonymizer

similar_datetime = lambda anon, obj, field, val: make_aware(anon.faker.datetime(field=field, val=val), utc)

empty_json_obj = lambda anon, obj, field, val: '{}'

class SocialAppAnonymizer(Anonymizer):

    model = SocialApp

    attributes = [
        ('id', "SKIP"),
        ('provider', "SKIP"),
        ('name', "SKIP"),
        ('client_id', "varchar"),
        ('key', "varchar"),
        ('secret', "varchar"),
    ]


class SocialAccountAnonymizer(Anonymizer):

    model = SocialAccount

    attributes = [
        ('id', "SKIP"),
        ('user_id', "SKIP"),
        ('provider', "SKIP"),
        ('uid', "varchar"),
        ('last_login', similar_datetime),
        ('date_joined', similar_datetime),
        ('extra_data', empty_json_obj),
    ]


class SocialTokenAnonymizer(Anonymizer):

    model = SocialToken

    attributes = [
        ('id', "SKIP"),
        ('app_id', "SKIP"),
        ('account_id', "SKIP"),
        ('token', "varchar"),
        ('token_secret', "varchar"),
        ('expires_at', similar_datetime),
    ]

