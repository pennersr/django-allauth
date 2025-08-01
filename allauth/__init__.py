r"""
    _        ___      __    __  .___________. __    __
 /\| |/\    /   \    |  |  |  | |           ||  |  |  |
 \ ` ' /   /  ^  \   |  |  |  | `---|  |----`|  |__|  |
|_     _| /  /_\  \  |  |  |  |     |  |     |   __   |
 / , . \ /  _____  \ |  `--'  |     |  |     |  |  |  |
 \/|_|\//__/     \__\ \______/      |__|     |__|  |__|

"""

VERSION = (65, 11, 0, "dev", 0)

__title__ = "django-allauth"
__version_info__ = VERSION
__version__ = ".".join(map(str, VERSION[:3])) + (
    "-{}{}".format(VERSION[3], VERSION[4] or "") if VERSION[3] != "final" else ""
)
__author__ = "Raymond Penners"
__license__ = "MIT"
__copyright__ = "Copyright 2010-2025 Raymond Penners and contributors"
