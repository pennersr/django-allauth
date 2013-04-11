# encoding: utf-8
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'SocialToken.socialaccount_socialtoken'
        db.alter_column('socialaccount_socialtoken', 'token', self.gf('django.db.models.fields.CharField')(max_length=250))

    def backwards(self, orm):

        # Changing field 'SocialToken.socialaccount_socialtoken'
        db.alter_column('socialaccount_socialtoken', 'token', self.gf('django.db.models.fields.CharField')(max_length=200))

    complete_apps = ['socialaccount']
