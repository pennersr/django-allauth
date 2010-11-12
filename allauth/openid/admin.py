from django.contrib import admin
from django.db import models
from django import forms

from models import OpenIDAccount

class OpenIDAccountAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)

    # If we ever switch back to TextField for storing OpenID identity
    # URLs...
    # formfield_overrides = {
    #    models.TextField: dict(widget=AdminURLFieldWidget)}
    
admin.site.register(OpenIDAccount, OpenIDAccountAdmin)

