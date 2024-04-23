#!/usr/bin/env python
import os


os.environ["DJANGO_SETTINGS_MODULE"] = "tests.settings"
from django.core import management


if __name__ == "__main__":
    management.execute_from_command_line()
