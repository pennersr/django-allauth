# encoding: utf-8
from south.db import db
from south.v2 import SchemaMigration

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Removing unique constraint on 'FacebookAccessToken', fields ['app', 'account']
        db.delete_unique('facebook_facebookaccesstoken', ['app_id', 'account_id'])

        # Deleting model 'FacebookApp'
        db.delete_table('facebook_facebookapp')

        # Deleting model 'FacebookAccessToken'
        db.delete_table('facebook_facebookaccesstoken')

        # Deleting model 'FacebookAccount'
        db.delete_table('facebook_facebookaccount')


    def backwards(self, orm):
        
        # Adding model 'FacebookApp'
        db.create_table('facebook_facebookapp', (
            ('application_id', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'])),
            ('api_key', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('application_secret', self.gf('django.db.models.fields.CharField')(max_length=80)),
        ))
        db.send_create_signal('facebook', ['FacebookApp'])

        # Adding model 'FacebookAccessToken'
        db.create_table('facebook_facebookaccesstoken', (
            ('access_token', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['facebook.FacebookAccount'])),
            ('app', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['facebook.FacebookApp'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('facebook', ['FacebookAccessToken'])

        # Adding unique constraint on 'FacebookAccessToken', fields ['app', 'account']
        db.create_unique('facebook_facebookaccesstoken', ['app_id', 'account_id'])

        # Adding model 'FacebookAccount'
        db.create_table('facebook_facebookaccount', (
            ('socialaccount_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['socialaccount.SocialAccount'], unique=True, primary_key=True)),
            ('social_id', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
            ('link', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('facebook', ['FacebookAccount'])


    models = {
        
    }

    complete_apps = ['facebook']
