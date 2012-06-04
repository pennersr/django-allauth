# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'TwitterAccount'
        db.delete_table('twitter_twitteraccount')

        # Deleting model 'TwitterApp'
        db.delete_table('twitter_twitterapp')


    def backwards(self, orm):
        
        # Adding model 'TwitterAccount'
        db.create_table('twitter_twitteraccount', (
            ('username', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('social_id', self.gf('django.db.models.fields.BigIntegerField')(unique=True)),
            ('socialaccount_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['socialaccount.SocialAccount'], unique=True, primary_key=True)),
            ('profile_image_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal('twitter', ['TwitterAccount'])

        # Adding model 'TwitterApp'
        db.create_table('twitter_twitterapp', (
            ('consumer_secret', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('request_token_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('authorize_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('consumer_key', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('access_token_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'])),
        ))
        db.send_create_signal('twitter', ['TwitterApp'])


    models = {
        
    }

    complete_apps = ['twitter']
