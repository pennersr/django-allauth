from django.contrib import admin

from models import OpenIDAccount

class OpenIDAccountAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)
    
admin.site.register(OpenIDAccount, OpenIDAccountAdmin)

