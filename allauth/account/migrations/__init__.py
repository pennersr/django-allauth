# The `account` app never had any South migrations, as the data models
# (specifically email uniqueness) depend on the settings, which is
# something that collides with South freezing mechanism.  For Django
# 1.7, we are able to provide migrations, but to stay backwards
# compatible we still need to make sure South does not pick up this
# `migrations` package. Therefore, let's do a bogus import which
# raises an ImportError in case South is used.

from django.db import migrations  # noqa
