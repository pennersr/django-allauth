SoundCloud
----------

SoundCloud allows you to choose between OAuth1 and OAuth2. Choose the latter.

App registration (get your key and secret here)
    http://soundcloud.com/you/apps/new

Development callback URL
    http://example.com/accounts/soundcloud/login/callback/


ID to URN Migration
^^^^^^^^^^^^^^^^^^^

Mid 2025, Soundcloud migrated away from using IDs for user accounts to URNs,
see: https://developers.soundcloud.com/blog/urn-num-to-string

Therefore, starting from 65.10.0, the allauth provider now uses the user ``urn``
instead of the ``id`` as the ID for social accounts.  If you have SoundCloud
already up and running, and are migration to allauth 65.10.0 or higher, you will
have to address this breaking change.  Consider migrating existing Soundcloud
SocialAccount records manually, for example, using::

    from django.db.models import F, Value
    from django.db.models.functions import Concat

    from allauth.socialaccount.models import SocialAccount


    SocialAccount.objects.filter(
        provider="soundcloud"
    ).exclude(
        uid__startswith="soundcloud:users:"
    ).update(
        uid=Concat(Value("soundcloud:users:"), F("uid"))
    )
