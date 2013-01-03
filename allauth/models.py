from django.db import models
from django.core.exceptions import ValidationError
import re

def is_valid_regex(value):
    try:
        re.compile(value)
    except re.error:
        raise ValidationError('"Expression" must be a valid regular expression.')

class BannedUsername(models.Model):
    expression = models.CharField(max_length=100, validators=[is_valid_regex])

    def match(self, username):
        return re.match(self.expression, username, flags=re.I)

    def __unicode__(self):
        return self.expression
