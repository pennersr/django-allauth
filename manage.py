#!/usr/bin/env python
import os

from django.core import management

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
    management.execute_from_command_line()
