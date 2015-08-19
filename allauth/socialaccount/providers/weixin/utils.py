import sys


PY2 = sys.version_info[0] == 2


if PY2:
    text_type = unicode
    iteritems = lambda d, *args, **kwargs: d.iteritems(*args, **kwargs)

    def to_native(x, charset=sys.getdefaultencoding(), errors='strict'):
        if x is None or isinstance(x, str):
            return x
        return x.encode(charset, errors)
else:
    text_type = str
    iteritems = lambda d, *args, **kwargs: iter(d.items(*args, **kwargs))

    def to_native(x, charset=sys.getdefaultencoding(), errors='strict'):
        if x is None or isinstance(x, str):
            return x
        return x.decode(charset, errors)

_always_safe = (b'abcdefghijklmnopqrstuvwxyz'
                b'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.-+')


def iter_multi_items(mapping):
    """
    Iterates over the items of a mapping yielding keys and values
    without dropping any from more complex structures.
    """
    if isinstance(mapping, dict):
        for key, value in iteritems(mapping):
            if isinstance(value, (tuple, list)):
                for value in value:
                    yield key, value
            else:
                yield key, value
    else:
        for item in mapping:
            yield item


def url_quote(string, charset='utf-8', errors='strict', safe='/:', unsafe=''):
    """
    URL encode a single string with a given encoding.

    :param s: the string to quote.
    :param charset: the charset to be used.
    :param safe: an optional sequence of safe characters.
    :param unsafe: an optional sequence of unsafe characters.

    .. versionadded:: 0.9.2
    The `unsafe` parameter was added.
    """
    if not isinstance(string, (text_type, bytes, bytearray)):
        string = text_type(string)
    if isinstance(string, text_type):
        string = string.encode(charset, errors)
    if isinstance(safe, text_type):
        safe = safe.encode(charset, errors)
    if isinstance(unsafe, text_type):
        unsafe = unsafe.encode(charset, errors)
    safe = frozenset(bytearray(safe) + _always_safe) - frozenset(bytearray(unsafe))
    rv = bytearray()
    for char in bytearray(string):
        if char in safe:
            rv.append(char)
        else:
            rv.extend(('%%%02X' % char).encode('ascii'))
    return to_native(bytes(rv))


def url_quote_plus(string, charset='utf-8', errors='strict', safe=''):
    return url_quote(string, charset, errors, safe + ' ', '+').replace(' ', '+')


def _url_encode_impl(obj, charset, encode_keys, sort, key):
    iterable = iter_multi_items(obj)
    if sort:
        iterable = sorted(iterable, key=key)
    for key, value in iterable:
        if value is None:
            continue
        if not isinstance(key, bytes):
            key = text_type(key).encode(charset)
        if not isinstance(value, bytes):
            value = text_type(value).encode(charset)
        yield url_quote_plus(key) + '=' + url_quote_plus(value)


def url_encode(obj, charset='utf-8', encode_keys=False, sort=False, key=None,
               separator=b'&'):
    separator = to_native(separator, 'ascii')
    return separator.join(_url_encode_impl(obj, charset, encode_keys, sort, key))
