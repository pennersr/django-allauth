import importlib
import random
import re
import string
import unicodedata
from collections import OrderedDict
from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.utils.encoding import force_str

from allauth import app_settings


# Magic number 7: if you run into collisions with this number, then you are
# of big enough scale to start investing in a decent user model...
MAX_USERNAME_SUFFIX_LENGTH = 7
USERNAME_SUFFIX_CHARS = [string.digits] * 4 + [string.ascii_letters] * (
    MAX_USERNAME_SUFFIX_LENGTH - 4
)


def _generate_unique_username_base(txts, regex=None):
    from .account.adapter import get_adapter

    adapter = get_adapter()
    username = None
    regex = regex or r"[^\w\s@+.-]"
    for txt in txts:
        if not txt:
            continue
        username = unicodedata.normalize("NFKD", force_str(txt))
        username = username.encode("ascii", "ignore").decode("ascii")
        if len(username) == 0:
            continue
        username = force_str(re.sub(regex, "", username).lower())
        # Django allows for '@' in usernames in order to accommodate for
        # project wanting to use email for username. In allauth we don't
        # use this, we already have a proper place for putting email
        # addresses (EmailAddress), so let's not use the full email
        # address and only take the part leading up to the '@'.
        username = username.split("@")[0]
        username = username.strip()
        username = re.sub(r"\s+", "_", username)
        # Finally, validating base username without database lookups etc.
        try:
            username = adapter.clean_username(username, shallow=True)
            break
        except ValidationError:
            pass
    return username or "user"


def get_username_max_length():
    from .account.app_settings import USER_MODEL_USERNAME_FIELD

    if USER_MODEL_USERNAME_FIELD is not None:
        User = get_user_model()
        max_length = User._meta.get_field(USER_MODEL_USERNAME_FIELD).max_length
    else:
        max_length = 0
    return max_length


def generate_username_candidate(basename, suffix_length):
    max_length = get_username_max_length()
    suffix = "".join(
        random.choice(USERNAME_SUFFIX_CHARS[i]) for i in range(suffix_length)  # nosec
    )
    return basename[0 : max_length - len(suffix)] + suffix


def generate_username_candidates(basename):
    from .account.app_settings import USERNAME_MIN_LENGTH

    if len(basename) >= USERNAME_MIN_LENGTH:
        ret = [basename]
    else:
        ret = []
    min_suffix_length = max(1, USERNAME_MIN_LENGTH - len(basename))
    max_suffix_length = min(get_username_max_length(), MAX_USERNAME_SUFFIX_LENGTH)
    for suffix_length in range(min_suffix_length, max_suffix_length):
        ret.append(generate_username_candidate(basename, suffix_length))
    return ret


def generate_unique_username(txts, regex=None):
    from allauth.account.utils import filter_users_by_username

    from .account.adapter import get_adapter
    from .account.app_settings import USER_MODEL_USERNAME_FIELD

    adapter = get_adapter()
    basename = _generate_unique_username_base(txts, regex)
    candidates = generate_username_candidates(basename)
    existing_usernames = filter_users_by_username(*candidates).values_list(
        USER_MODEL_USERNAME_FIELD, flat=True
    )
    existing_usernames = set([n.lower() for n in existing_usernames])
    for candidate in candidates:
        if candidate.lower() not in existing_usernames:
            try:
                return adapter.clean_username(candidate, shallow=True)
            except ValidationError:
                pass
    # This really should not happen
    raise NotImplementedError("Unable to find a unique username")


def import_attribute(path):
    assert isinstance(path, str)  # nosec
    pkg, attr = path.rsplit(".", 1)
    ret = getattr(importlib.import_module(pkg), attr)
    return ret


def import_callable(path_or_callable):
    if not callable(path_or_callable):
        ret = import_attribute(path_or_callable)
    else:
        ret = path_or_callable
    return ret


def set_form_field_order(form, field_order):
    """
    This function is a verbatim copy of django.forms.Form.order_fields() to
    support field ordering below Django 1.9.

    field_order is a list of field names specifying the order. Append fields
    not included in the list in the default order for backward compatibility
    with subclasses not overriding field_order. If field_order is None, keep
    all fields in the order defined in the class. Ignore unknown fields in
    field_order to allow disabling fields in form subclasses without
    redefining ordering.
    """
    if field_order is None:
        return
    fields = OrderedDict()
    for key in field_order:
        try:
            fields[key] = form.fields.pop(key)
        except KeyError:  # ignore unknown fields
            pass
    fields.update(form.fields)  # add remaining fields in original order
    form.fields = fields


def build_absolute_uri(request, location, protocol=None):
    """request.build_absolute_uri() helper

    Like request.build_absolute_uri, but gracefully handling
    the case where request is None.
    """
    from .account import app_settings as account_settings

    if request is None:
        if not app_settings.SITES_ENABLED:
            raise ImproperlyConfigured(
                "Passing `request=None` requires `sites` to be enabled."
            )
        from django.contrib.sites.models import Site

        site = Site.objects.get_current()
        bits = urlsplit(location)
        if not (bits.scheme and bits.netloc):
            uri = "{proto}://{domain}{url}".format(
                proto=account_settings.DEFAULT_HTTP_PROTOCOL,
                domain=site.domain,
                url=location,
            )
        else:
            uri = location
    else:
        uri = request.build_absolute_uri(location)
    # NOTE: We only force a protocol if we are instructed to do so
    # (via the `protocol` parameter, or, if the default is set to
    # HTTPS. The latter keeps compatibility with the debatable use
    # case of running your site under both HTTP and HTTPS, where one
    # would want to make sure HTTPS links end up in password reset
    # mails even while they were initiated on an HTTP password reset
    # form.
    if not protocol and account_settings.DEFAULT_HTTP_PROTOCOL == "https":
        protocol = account_settings.DEFAULT_HTTP_PROTOCOL
    # (end NOTE)
    if protocol:
        uri = protocol + ":" + uri.partition(":")[2]
    return uri


def get_form_class(forms, form_id, default_form):
    form_class = forms.get(form_id, default_form)
    if isinstance(form_class, str):
        form_class = import_attribute(form_class)
    return form_class


def get_request_param(request, param, default=None):
    if request is None:
        return default
    return request.POST.get(param) or request.GET.get(param, default)


def get_setting(name, dflt):
    getter = getattr(
        settings,
        "ALLAUTH_SETTING_GETTER",
        lambda name, dflt: getattr(settings, name, dflt),
    )
    getter = import_callable(getter)
    return getter(name, dflt)
