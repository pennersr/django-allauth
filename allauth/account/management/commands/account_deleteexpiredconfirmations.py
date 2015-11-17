from django.core.management.base import BaseCommand
from allauth.account.models import EmailConfirmation


class Command(BaseCommand):
    def handle(self, *args, **options):
        expired_confirmations_count = EmailConfirmation.objects.all_expired().count()
        EmailConfirmation.objects.delete_expired_confirmations()
        print ("Removed %s expired email confirmations." % expired_confirmations_count)
