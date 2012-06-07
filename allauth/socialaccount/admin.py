from django.contrib import admin

from models import SocialApp, SocialAccount, SocialToken


class SocialAppAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider', 'site')


class SocialAccountAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)
    list_display = ('user', 'uid', 'provider')


class SocialTokenAdmin(admin.ModelAdmin):
    raw_id_fields = ('app', 'account',)
    list_display = ('app', 'account', 'token')

admin.site.register(SocialApp, SocialAppAdmin)
admin.site.register(SocialToken, SocialTokenAdmin)
admin.site.register(SocialAccount, SocialAccountAdmin)
