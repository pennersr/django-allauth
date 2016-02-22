#!/usr/bin/env python

"""This script runs makemessages to update the .po files based on source code,
and then it runs compilemessages to update the .mo files based on the .po
files.

It's here as a script so that some customisations can be made, and so that it's
painless to run again in future. This should be run every time there is a
change in source code that affects i18n, and every time the translations in the
.po files have been changed or updated.
"""


from __future__ import print_function
import sys
import os
import subprocess
import logging


def main():
    if len(sys.argv) > 1:
        raise(Exception("No command-line arguments expected"))
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    root_path = os.path.dirname(os.path.realpath(__file__))
    package_path = os.path.join(root_path, "allauth")
    logging.info("Changing directory to %s" % (package_path,))
    os.chdir(package_path)

    logging.info("Running makemessages")
    subprocess.check_call([
        sys.executable,
        os.path.join(root_path, "manage.py"),
        "makemessages",
        "--all",
        # "--verbosity", "3",
    ])

    logging.info("Running compilemessages")
    subprocess.check_call([
        sys.executable,
        os.path.join(root_path, "manage.py"),
        "compilemessages",
        # "--verbosity", "3",
    ])

    logging.info("Script done")

if __name__ == "__main__":
    main()
