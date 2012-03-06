from django.contrib import admin

from models import TwitterApp, TwitterAccount

class TwitterAppAdmin(admin.ModelAdmin):
    fields = ('site', 'name', 'consumer_key', 'consumer_secret', 'request_token_url', 'authorize_url', 'access_token_url')

class TwitterAccountAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)

admin.site.register(TwitterApp, TwitterAppAdmin)
admin.site.register(TwitterAccount, TwitterAccountAdmin)

