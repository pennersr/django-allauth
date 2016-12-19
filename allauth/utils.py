import random
import string
import base64
import re
import unicodedata
import json
from collections import OrderedDict

from django.core.exceptions import ImproperlyConfigured
from django.core.validators import validate_email, ValidationError
from django.contrib.sites.models import Site
from django.db.models import FieldDoesNotExist, FileField
from django.db.models.fields import (DateTimeField, DateField,
                                     EmailField, TimeField,
                                     BinaryField)
from django.utils import six, dateparse
from django.utils.six.moves.urllib.parse import urlsplit

from django.core.serializers.json import DjangoJSONEncoder
try:
    from django.utils.encoding import force_text, force_bytes
except ImportError:
    from django.utils.encoding import force_unicode as force_text
from allauth.compat import importlib, reverse, NoReverseMatch


# Magic number 7: if you run into collisions with this number, then you are
# of big enough scale to start investing in a decent user model...
MAX_USERNAME_SUFFIX_LENGTH = 7
USERNAME_SUFFIX_CHARS = (
    [string.digits] * 4 +
    [string.ascii_letters] * (MAX_USERNAME_SUFFIX_LENGTH - 4))


def _generate_unique_username_base(txts, regex=None):
    from .account.adapter import get_adapter
    adapter = get_adapter()
    username = None
    regex = regex or '[^\w\s@+.-]'
    for txt in txts:
        if not txt:
            continue
        username = unicodedata.normalize('NFKD', force_text(txt))
        username = username.encode('ascii', 'ignore').decode('ascii')
        username = force_text(re.sub(regex, '', username).lower())
        # Django allows for '@' in usernames in order to accomodate for
        # project wanting to use e-mail for username. In allauth we don't
        # use this, we already have a proper place for putting e-mail
        # addresses (EmailAddress), so let's not use the full e-mail
        # address and only take the part leading up to the '@'.
        username = username.split('@')[0]
        username = username.strip()
        username = re.sub('\s+', '_', username)
        # Finally, validating base username without database lookups etc.
        try:
            username = adapter.clean_username(username, shallow=True)
            break
        except ValidationError:
            pass
    return username or 'user'


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
    suffix = ''.join(
        random.choice(USERNAME_SUFFIX_CHARS[i])
        for i in range(suffix_length))
    return basename[0:max_length - len(suffix)] + suffix


def generate_username_candidates(basename):
    ret = [basename]
    max_suffix_length = min(
        get_username_max_length(),
        MAX_USERNAME_SUFFIX_LENGTH)
    for suffix_length in range(2, max_suffix_length):
        ret.append(generate_username_candidate(basename, suffix_length))
    return ret


def generate_unique_username(txts, regex=None):
    from .account.app_settings import USER_MODEL_USERNAME_FIELD
    from .account.adapter import get_adapter
    from allauth.account.utils import filter_users_by_username

    adapter = get_adapter()
    basename = _generate_unique_username_base(txts, regex)
    candidates = generate_username_candidates(basename)
    existing_users = filter_users_by_username(*candidates).values_list(
        USER_MODEL_USERNAME_FIELD, flat=True)
    for candidate in candidates:
        if candidate not in existing_users:
            try:
                return adapter.clean_username(candidate, shallow=True)
            except ValidationError:
                pass
    # This really should not happen
    raise NotImplementedError('Unable to find a unique username')


def valid_email_or_none(email):
    ret = None
    try:
        if email:
            validate_email(email)
            if len(email) <= EmailField().max_length:
                ret = email
    except ValidationError:
        pass
    return ret


def email_address_exists(email, exclude_user=None):
    from .account import app_settings as account_settings
    from .account.models import EmailAddress

    emailaddresses = EmailAddress.objects
    if exclude_user:
        emailaddresses = emailaddresses.exclude(user=exclude_user)
    ret = emailaddresses.filter(email__iexact=email).exists()
    if not ret:
        email_field = account_settings.USER_MODEL_EMAIL_FIELD
        if email_field:
            users = get_user_model().objects
            if exclude_user:
                users = users.exclude(pk=exclude_user.pk)
            ret = users.filter(**{email_field+'__iexact': email}).exists()
    return ret


def import_attribute(path):
    assert isinstance(path, six.string_types)
    pkg, attr = path.rsplit('.', 1)
    ret = getattr(importlib.import_module(pkg), attr)
    return ret


def import_callable(path_or_callable):
    if not hasattr(path_or_callable, '__call__'):
        ret = import_attribute(path_or_callable)
    else:
        ret = path_or_callable
    return ret


try:
    from django.contrib.auth import get_user_model
except ImportError:
    # To keep compatibility with Django 1.4
    def get_user_model():
        from . import app_settings
        from django.db.models import get_model

        try:
            app_label, model_name = app_settings.USER_MODEL.split('.')
        except ValueError:
            raise ImproperlyConfigured("AUTH_USER_MODEL must be of the"
                                       " form 'app_label.model_name'")
        user_model = get_model(app_label, model_name)
        if user_model is None:
            raise ImproperlyConfigured("AUTH_USER_MODEL refers to model"
                                       " '%s' that has not been installed"
                                       % app_settings.USER_MODEL)
        return user_model


def get_current_site(request=None):
    """Wrapper around ``Site.objects.get_current`` to handle ``Site`` lookups
    by request in Django >= 1.8.

    :param request: optional request object
    :type request: :class:`django.http.HttpRequest`
    """
    # >= django 1.8
    if request and hasattr(Site.objects, '_get_site_by_request'):
        site = Site.objects.get_current(request=request)
    else:
        site = Site.objects.get_current()

    return site


def resolve_url(to):
    """
    Subset of django.shortcuts.resolve_url (that one is 1.5+)
    """
    try:
        return reverse(to)
    except NoReverseMatch:
        # If this doesn't "feel" like a URL, re-raise.
        if '/' not in to and '.' not in to:
            raise
    # Finally, fall back and assume it's a URL
    return to


SERIALIZED_DB_FIELD_PREFIX = '_db_'


def serialize_instance(instance):
    """
    Since Django 1.6 items added to the session are no longer pickled,
    but JSON encoded by default. We are storing partially complete models
    in the session (user, account, token, ...). We cannot use standard
    Django serialization, as these are models are not "complete" yet.
    Serialization will start complaining about missing relations et al.
    """
    data = {}
    for k, v in instance.__dict__.items():
        if k.startswith('_') or callable(v):
            continue
        try:
            field = instance._meta.get_field(k)
            if isinstance(field, BinaryField):
                v = force_text(base64.b64encode(v))
            elif isinstance(field, FileField):
                if v and not isinstance(v, six.string_types):
                    v = v.name
            # Check if the field is serializable. If not, we'll fall back
            # to serializing the DB values which should cover most use cases.
            try:
                json.dumps(v, cls=DjangoJSONEncoder)
            except TypeError:
                v = field.get_prep_value(v)
                k = SERIALIZED_DB_FIELD_PREFIX + k
        except FieldDoesNotExist:
            pass
        data[k] = v
    return json.loads(json.dumps(data, cls=DjangoJSONEncoder))


def deserialize_instance(model, data):
    ret = model()
    for k, v in data.items():
        is_db_value = False
        if k.startswith(SERIALIZED_DB_FIELD_PREFIX):
            k = k[len(SERIALIZED_DB_FIELD_PREFIX):]
            is_db_value = True
        if v is not None:
            try:
                f = model._meta.get_field(k)
                if isinstance(f, DateTimeField):
                    v = dateparse.parse_datetime(v)
                elif isinstance(f, TimeField):
                    v = dateparse.parse_time(v)
                elif isinstance(f, DateField):
                    v = dateparse.parse_date(v)
                elif isinstance(f, BinaryField):
                    v = force_bytes(
                        base64.b64decode(
                            force_bytes(v)))
                elif is_db_value:
                    try:
                        # This is quite an ugly hack, but will cover most
                        # use cases...
                        v = f.from_db_value(v, None, None, None)
                    except:
                        raise ImproperlyConfigured(
                            "Unable to auto serialize field '{}', custom"
                            " serialization override required".format(k)
                        )
            except FieldDoesNotExist:
                pass
        setattr(ret, k, v)
    return ret


def set_form_field_order(form, fields_order):
    assert isinstance(form.fields, OrderedDict)
    form.fields = OrderedDict(
        (f, form.fields[f])
        for f in fields_order)


def build_absolute_uri(request, location, protocol=None):
    """request.build_absolute_uri() helper

    Like request.build_absolute_uri, but gracefully handling
    the case where request is None.
    """
    from .account import app_settings as account_settings

    if request is None:
        site = get_current_site()
        bits = urlsplit(location)
        if not (bits.scheme and bits.netloc):
            uri = '{proto}://{domain}{url}'.format(
                proto=account_settings.DEFAULT_HTTP_PROTOCOL,
                domain=site.domain,
                url=location)
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
    if not protocol and account_settings.DEFAULT_HTTP_PROTOCOL == 'https':
        protocol = account_settings.DEFAULT_HTTP_PROTOCOL
    # (end NOTE)
    if protocol:
        uri = protocol + ':' + uri.partition(':')[2]
    return uri


def get_form_class(forms, form_id, default_form):
    form_class = forms.get(form_id, default_form)
    if isinstance(form_class, six.string_types):
        form_class = import_attribute(form_class)
    return form_class


def get_request_param(request, param, default=None):
    return request.POST.get(param) or request.GET.get(param, default)
