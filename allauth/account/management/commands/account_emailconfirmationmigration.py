from django.core.management.base import BaseCommand, CommandError

from allauth.account.models import EmailAddress, EmailConfirmation

class Command(BaseCommand):
    def handle(self, *args, **options):
        if True:
            EmailAddress.objects.all().delete()
        if EmailAddress.objects.all().exists():
            raise CommandError('New-style EmailAddress objects exist, please delete those first')
        self.migrate_email_address()
        self.migrate_email_confirmation()

    def migrate_email_address(self):
        for email_address in EmailAddress.objects.raw('SELECT * from emailconfirmation_emailaddress'):
            email_address.save()

    def migrate_email_confirmation(self):
        for email_confirmation in EmailConfirmation.objects.raw('SELECT id, email_address_id, sent, confirmation_key as key from emailconfirmation_emailconfirmation'):
            email_confirmation.created = email_confirmation.sent
            email_confirmation.save()


            
