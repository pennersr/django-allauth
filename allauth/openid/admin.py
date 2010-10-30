from django.contrib import admin
from django.contrib.admin.widgets import AdminURLFieldWidget
from django.db import models
from django import forms

from models import OpenIDAccount

class OpenIDAccountAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)
    formfield_overrides = {
        models.TextField: dict(widget=AdminURLFieldWidget)}
    
admin.site.register(OpenIDAccount, OpenIDAccountAdmin)

