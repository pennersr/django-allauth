from django.contrib import admin

from .models import OpenIDNonce, OpenIDStore


class OpenIDStoreAdmin(admin.ModelAdmin):
    pass


class OpenIDNonceAdmin(admin.ModelAdmin):
    pass


admin.site.register(OpenIDStore, OpenIDStoreAdmin)
admin.site.register(OpenIDNonce, OpenIDNonceAdmin)
