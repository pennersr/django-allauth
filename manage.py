#!/usr/bin/env python
import os


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.regular.settings")
from django.core import management  # noqa: E402


if __name__ == "__main__":
    management.execute_from_command_line()
