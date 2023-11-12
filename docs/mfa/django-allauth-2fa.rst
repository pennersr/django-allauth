Upgrading from django-allauth-2fa
=================================

In case you are currently using django-allauth-2fa and want to switch to the
built-in implementation, you will need to migrate the existing TOTP keys and recovery codes. For that purpose, the following reference code is available::

    import base64

    from allauth.mfa.adapter import get_adapter
    from allauth.mfa.models import Authenticator
    from django.core.management.base import BaseCommand
    from django_otp.plugins.otp_static.models import StaticDevice
    from django_otp.plugins.otp_totp.models import TOTPDevice


    class Command(BaseCommand):
        def handle(self, **options):
            adapter = get_adapter()
            authenticators = []
            for totp in TOTPDevice.objects.filter(confirmed=True).iterator():
                recovery_codes = set()
                for sdevice in StaticDevice.objects.filter(confirmed=True, user_id=totp.user_id).iterator():
                    recovery_codes.update(sdevice.token_set.values_list("token", flat=True))
                secret = base64.b32encode(bytes.fromhex(totp.key)).decode("ascii")
                totp_authenticator = Authenticator(
                    user_id=totp.user_id,
                    type=Authenticator.Type.TOTP,
                    data={"secret": adapter.encrypt(secret)},
                )
                authenticators.append(totp_authenticator)
                authenticators.append(
                    Authenticator(
                        user_id=totp.user_id,
                        type=Authenticator.Type.RECOVERY_CODES,
                        data={
                            "migrated_codes": [adapter.encrypt(c) for c in recovery_codes],
                        },
                    )
                )
            Authenticator.objects.bulk_create(authenticators)
