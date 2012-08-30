from django.core.management.base import BaseCommand, CommandError
from django.core.management.color import no_style
from django.db import connections

from allauth.account import app_settings
from allauth.account.models import EmailAddress, EmailConfirmation

class Command(BaseCommand):
    def handle(self, *args, **options):
        if False:
            EmailAddress.objects.all().delete()

        if EmailAddress.objects.all().exists():
            raise CommandError('New-style EmailAddress objects exist, please delete those first')

        self.migrate_email_address()
        self.migrate_email_confirmation()
        self.reset_sequences()

    def reset_sequences(self):
        connection = connections['default']
        cursor = connection.cursor()
        style = no_style()
        sequence_sql = connection.ops.sequence_reset_sql(style, 
                                                         [EmailAddress,
                                                          EmailConfirmation])
        if sequence_sql:
            print "Resetting sequences"
            for line in sequence_sql:
                cursor.execute(line)


    def migrate_email_address(self):
        seen_emails = {}
        # Poor man's conflict handling: prefer latest (hence order by)
        for email_address in EmailAddress.objects.raw('SELECT * from emailconfirmation_emailaddress order by id desc'):
            if app_settings.UNIQUE_EMAIL and email_address.email in seen_emails:
                print 'Duplicate e-mail address skipped: %s collides with %s' % (email_address, seen_emails[email_address.email])
                continue
            seen_emails[email_address.email] = email_address
            email_address.save()

    def migrate_email_confirmation(self):
        seen_keys = set()
        for email_confirmation in EmailConfirmation.objects.raw('SELECT id, email_address_id, sent, confirmation_key as key from emailconfirmation_emailconfirmation'):
            email_confirmation.created = email_confirmation.sent
            if EmailAddress.objects.filter(id=email_confirmation.email_address_id).exists():
                if email_confirmation.key in seen_keys:
                    print 'Could not migrate EmailConfirmation %d due to duplicate key' % email_confirmation.id
                    continue
                seen_keys.add(email_confirmation.key)
                email_confirmation.save()
            else:
                print ('Could not migrate EmailConfirmation %d due to missing EmailAddress' % email_confirmation.id)



            
