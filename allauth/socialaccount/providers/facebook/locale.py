# Default locale mapping for the Facebook JS SDK
# The list of supported locales is at
# https://www.facebook.com/translations/FacebookLocales.xml
import os

from django.utils.translation import get_language, to_locale


def _build_locale_table(filename_or_file):
    """
    Parses the FacebookLocales.xml file and builds a dict relating every
    available language ('en, 'es, 'zh', ...) with a list of available regions
    for that language ('en' -> 'US', 'EN') and an (arbitrary) default region.
    """
    # Require the XML parser module only if we want the default mapping
    from xml.dom.minidom import parse

    dom = parse(filename_or_file)

    reps = dom.getElementsByTagName('representation')
    locs = map(lambda r: r.childNodes[0].data, reps)

    locale_map = {}
    for loc in locs:
        lang, _, reg = loc.partition('_')
        lang_map = locale_map.setdefault(lang, {'regs': [], 'default': reg})
        lang_map['regs'].append(reg)

    # Default region overrides (arbitrary)
    locale_map['en']['default'] = 'US'
    # Special case: Use es_ES for Spain and es_LA for everything else
    locale_map['es']['default'] = 'LA'
    locale_map['zh']['default'] = 'CN'
    locale_map['fr']['default'] = 'FR'
    locale_map['pt']['default'] = 'PT'

    return locale_map


def get_default_locale_callable():
    """
    Wrapper function so that the default mapping is only built when needed
    """
    exec_dir = os.path.dirname(os.path.realpath(__file__))
    xml_path = os.path.join(exec_dir, 'data', 'FacebookLocales.xml')

    fb_locales = _build_locale_table(xml_path)

    def default_locale(request):
        """
        Guess an appropriate FB locale based on the active Django locale.
        If the active locale is available, it is returned. Otherwise,
        it tries to return another locale with the same language. If there
        isn't one avaible, 'en_US' is returned.
        """
        chosen = 'en_US'
        language = get_language()
        if language:
            locale = to_locale(language)
            lang, _, reg = locale.partition('_')

            lang_map = fb_locales.get(lang)
            if lang_map is not None:
                if reg in lang_map['regs']:
                    chosen = lang + '_' + reg
                else:
                    chosen = lang + '_' + lang_map['default']
        return chosen

    return default_locale
