from django.contrib import admin

from models import FacebookApp, FacebookAccount, FacebookAccessToken

class FacebookAccountAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)
    list_display = ('user', 'social_id', 'name')

class FacebookAccessTokenAdmin(admin.ModelAdmin):
    raw_id_fields = ('account',)
    
admin.site.register(FacebookApp)
admin.site.register(FacebookAccount, FacebookAccountAdmin)
admin.site.register(FacebookAccessToken, FacebookAccessTokenAdmin)

