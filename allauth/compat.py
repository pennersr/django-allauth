try:
    from django.utils.six.moves.urllib.parse import urlsplit
except ImportError:
    from urllib.parse import urlsplit  # noqa

try:
    from django.utils import six
except ImportError:
    class six:
        PY3 = True
        PY2 = False
        integer_types = (int,)
        string_types = (str,)


try:
    from collections import UserDict
except ImportError:
    from UserDict import UserDict  # noqa

try:
    from urllib.parse import parse_qsl, parse_qs, urlparse, urlunparse, urljoin
except ImportError:
    from urlparse import parse_qsl, parse_qs, urlparse, urlunparse, urljoin  # noqa

try:
    from django.utils.encoding import python_2_unicode_compatible
except ImportError:
    def python_2_unicode_compatible(c):
        return c

if six.PY2:
    from django.utils.encoding import force_text as force_str
else:
    try:
        from django.utils.encoding import force_str
    except ImportError:
        from django.utils.encoding import force_text as force_str  # noqa


def int_to_base36(i):
    """
    Django on py2 raises ValueError on large values.
    """
    if six.PY2:
        char_set = '0123456789abcdefghijklmnopqrstuvwxyz'
        if i < 0:
            raise ValueError("Negative base36 conversion input.")
        if not isinstance(i, six.integer_types):
            raise TypeError("Non-integer base36 conversion input.")
        if i < 36:
            return char_set[i]
        b36 = ''
        while i != 0:
            i, n = divmod(i, 36)
            b36 = char_set[n] + b36
    else:
        from django.utils.http import int_to_base36
        b36 = int_to_base36(i)
    return b36


def base36_to_int(s):
    if six.PY2:
        if len(s) > 13:
            raise ValueError("Base36 input too large")
        value = int(s, 36)
    else:
        from django.utils.http import base36_to_int
        value = base36_to_int(s)
    return value


if six.PY3:
    from django.utils.translation import gettext as ugettext  # noqa
    from django.utils.translation import gettext_lazy as ugettext_lazy  # noqa
else:
    from django.utils.translation import ugettext  # noqa
    from django.utils.translation import ugettext_lazy  # noqa
