from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class Scope(object):
    USERINFO_PROFILE = '/authenticate'


class OrcidAccount(ProviderAccount):
    def get_profile_url(self):
        return extract_from_dict(self.account.extra_data,
                                 ['orcid-profile', 'orcid-identifier', 'uri'])

    def to_str(self):
        dflt = super(OrcidAccount, self).to_str()
        return self.account.uid


class OrcidProvider(OAuth2Provider):
    id = 'orcid'
    name = 'Orcid.org'
    package = 'allauth.socialaccount.providers.orcid'
    account_class = OrcidAccount

    def get_default_scope(self):
        return [Scope.USERINFO_PROFILE]

    def extract_uid(self, data):
        return extract_from_dict(data, ['orcid-profile', 'orcid-identifier',
                                        'path'])

    def extract_common_fields(self, data):
        common_fields = dict(
            email=extract_from_dict(data, ['orcid-profile', 'orcid-bio',
                                           'contact-details', 'email', 0,
                                           'value']),
            last_name=extract_from_dict(data, ['orcid-profile', 'orcid-bio',
                                               'personal-details',
                                               'family-name', 'value']),
            first_name=extract_from_dict(data, ['orcid-profile',
                                                'orcid-bio',
                                                'personal-details',
                                                'given-names', 'value']),)
        return dict((key, value) for (key, value) in common_fields.items()
                    if value)

providers.registry.register(OrcidProvider)


def extract_from_dict(data, path):
    """
    Navigate `data`, a multidimensional array (list or dictionary), and returns
    the object at `path`.
    """
    value = data
    try:
        for key in path:
            value = value[key]
        return value
    except (KeyError, IndexError):
        return ''
