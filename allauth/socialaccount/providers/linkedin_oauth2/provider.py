from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.base import (
    ProviderAccount,
    ProviderException,
)
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


DEFAULT_LOCALE = 'en_US'


def get_locale(preferred_locale):
    if (preferred_locale is None
            or 'country' not in preferred_locale
            or 'language' not in preferred_locale):
        return DEFAULT_LOCALE

    return '_'.join(
        [preferred_locale.get('language'), preferred_locale.get('country')]
    )

def parse_name_field(field_name, data):
    field = data.get(field_name, None)

    if (not field
            or 'preferredLocale' not in field
            or 'localized' not in field):
        return ''

    locale = get_locale(field.get('preferredLocale'))

    return field.get('localized').get(locale, '')

def has_email(data):
    return ('elements' in data
            and len(data['elements']) > 0
            and 'handle~' in data.get('elements')[0]
            and 'emailAddress' in data.get('elements')[0].get('handle~'))

def parse_email_field(data):
    if not has_email(data):
        return ''

    return data.get('elements')[0].get('handle~').get('emailAddress')

class LinkedInOAuth2Account(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get('publicProfileUrl')

    def get_avatar_url(self):
        avatar_url = ''

        # the highest res picture should be the last one in the list
        try:
            avatar_url = (
                self.account.extra_data
                    .get('profilePicture')
                    .get('displayImage~')
                    .get('elements')[-1]
                    .get('identifiers')[0]
                    .get('identifier')
            )
        except Exception:
            pass

        return avatar_url

    def to_str(self):
        dflt = super(LinkedInOAuth2Account, self).to_str()
        name = self.account.extra_data.get('name', dflt)
        first_name = self.account.extra_data.get('firstName', None)
        last_name = self.account.extra_data.get('lastName', None)
        if first_name and last_name:
            name = first_name + ' ' + last_name
        return name


class LinkedInOAuth2Provider(OAuth2Provider):
    id = 'linkedin_oauth2'
    # Name is displayed to ordinary users -- don't include protocol
    name = 'LinkedIn'
    account_class = LinkedInOAuth2Account
    fields_map = {
        'id': 'id',
        'first-name': 'firstName',
        'last-name': 'lastName',
        'picture-url': 'profilePicture(displayImage~:playableStreams)'
    }

    def get_mapped_field(self, field):
        if field not in self.fields_map:
            return field
        return self.fields_map[field]

    def extract_uid(self, data):
        if 'id' not in data:
            raise ProviderException(
                'LinkedIn encountered an internal error while logging in. \
                Please try again.'
            )
        return str(data['id'])

    def get_profile_fields(self):
        default_fields = ['id',
                          'first-name',
                          'last-name',
                          'picture-url']
        fields = self.get_settings().get('PROFILE_FIELDS',
                                         default_fields)

        return [self.get_mapped_field(field) for field in fields]

    def get_default_scope(self):
        scope = ['r_liteprofile']
        if app_settings.QUERY_EMAIL:
            scope.append('r_emailaddress')
        return scope

    def extract_common_fields(self, data):
        first_name = parse_name_field('firstName', data)
        last_name = parse_name_field('lastName', data)
        email = parse_email_field(data)

        return dict(email=email,
                    first_name=first_name,
                    last_name=last_name)


provider_classes = [LinkedInOAuth2Provider]
