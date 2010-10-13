from django.contrib import admin

from models import TwitterApp, TwitterAccount

class TwitterAccountAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)
    
admin.site.register(TwitterApp)
admin.site.register(TwitterAccount, TwitterAccountAdmin)

