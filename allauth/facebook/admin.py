from django.contrib import admin

from models import FacebookApp, FacebookAccount

class FacebookAccountAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)
    
admin.site.register(FacebookApp)
admin.site.register(FacebookAccount, FacebookAccountAdmin)

