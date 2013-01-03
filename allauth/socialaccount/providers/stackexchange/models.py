from django.db import models

class StackExchangeSite(models.Model):
    SITE_STATES = (
        ('normal', 'Normal'),
        ('closed_beta', 'Closed Beta'),
        ('open_beta', 'Open Beta'),
        ('linked_meta', 'Linked Meta'),
    )
    SITE_TYPES = (
        ('main_site', 'Main Site'),
        ('meta_site', 'Meta Site'),
    )
    api_site_parameter = models.CharField(max_length=30)
    audience = models.CharField(max_length=200)
    favicon_url = models.URLField()
    icon_url = models.URLField()
    launch_date = models.DateTimeField()
    logo_url = models.URLField()
    name = models.CharField(max_length=30)
    site_state = models.CharField(max_length=20, choices=SITE_STATES)
    site_type = models.CharField(max_length=20, choices=SITE_TYPES)
    site_url = models.URLField()
    styling_link_color = models.CharField(max_length=7)
    styling_tag_foreground_color = models.CharField(max_length=7)
    styling_tag_background_color = models.CharField(max_length=7)
