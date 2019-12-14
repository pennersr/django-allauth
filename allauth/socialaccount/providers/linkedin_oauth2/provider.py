from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.base import (
    ProviderAccount,
    ProviderException,
)
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


def _extract_name_field(data, field_name):
    ret = ''
    v = data.get(field_name, {})
    if v:
        if isinstance(v, str):
            # Old V1 data
            ret = v
        else:
            localized = v.get('localized', {})
            preferred_locale = v.get(
                'preferredLocale', {'country': 'US', 'language': 'en'})
            locale_key = '_'.join([
                preferred_locale['language'],
                preferred_locale['country']])
            if locale_key in localized:
                ret = localized.get(locale_key)
            elif localized:
                ret = next(iter(localized.values()))
    return ret


def _extract_email(data):
    """
    {'elements': [{'handle': 'urn:li:emailAddress:319371470',
               'handle~': {'emailAddress': 'raymond.penners@intenct.nl'}}]}
    """
    ret = ''
    elements = data.get('elements', [])
    if len(elements) > 0:
        ret = elements[0].get('handle~', {}).get('emailAddress', '')
    return ret


class LinkedInOAuth2Account(ProviderAccount):
    def to_str(self):
        ret = super(LinkedInOAuth2Account, self).to_str()
        first_name = _extract_name_field(self.account.extra_data, 'firstName')
        last_name = _extract_name_field(self.account.extra_data, 'lastName')
        if first_name or last_name:
            ret = ' '.join([first_name, last_name]).strip()
        return ret

    def get_avatar_url(self):
        """
        Attempts the load the avatar associated to the avatar.

        Requires the `profilePicture(displayImage~:playableStreams)`
        profile field configured in settings.py

        :return:
        """
        provider_configuration = self.account.get_provider().get_settings()
        configured_profile_fields = \
            provider_configuration.get('PROFILE_FIELDS', [])
        # Can't get the avatar when this field is not specified
        picture_field = 'profilePicture(displayImage~:playableStreams)'
        if picture_field not in configured_profile_fields:
            return super(LinkedInOAuth2Account, self).get_avatar_url()
        # Iterate over the fields and attempt to get it by configured size
        profile_picture_config = \
            provider_configuration.get('PROFILEPICTURE', {})
        req_size = \
            profile_picture_config.get('display_size_w_h', (100.0, 100.0))
        req_auth_method = \
            profile_picture_config.get('authorization_method', 'PUBLIC')
        # Iterate over the data returned by the provider
        profile_elements = self.account.extra_data\
            .get('profilePicture', {})\
            .get('displayImage~', {})\
            .get('elements', [])
        for single_element in profile_elements:
            if not req_auth_method == single_element['authorizationMethod']:
                continue
            # Get the dimensions from the payload
            image_data = single_element.get('data', {})\
                .get('com.linkedin.digitalmedia.mediaartifact.StillImage', {})\
                .get('displaySize', {})
            if not image_data:
                continue
            width, height = image_data['width'], image_data['height']
            if not width or not height:
                continue
            if not width == req_size[0] or not height == req_size[1]:
                continue
            # Get the uri since actual size matches the requested size.
            to_return = single_element.get('identifiers', [{}, ])[0]\
                .get('identifier')
            if to_return:
                return to_return
        return super(LinkedInOAuth2Account, self).get_avatar_url()


class LinkedInOAuth2Provider(OAuth2Provider):
    id = 'linkedin_oauth2'
    # Name is displayed to ordinary users -- don't include protocol
    name = 'LinkedIn'
    account_class = LinkedInOAuth2Account

    def extract_uid(self, data):
        if 'id' not in data:
            raise ProviderException(
                'LinkedIn encountered an internal error while logging in. \
                Please try again.'
            )
        return str(data['id'])

    def get_profile_fields(self):
        default_fields = [
            'id',
            'firstName',
            'lastName',
            # This would be needed to in case you need access to the image
            # URL. Not enabling this by default due to the amount of data
            # returned.
            #
            # 'profilePicture(displayImage~:playableStreams)'
        ]
        fields = self.get_settings().get('PROFILE_FIELDS',
                                         default_fields)
        return fields

    def get_default_scope(self):
        scope = ['r_liteprofile']
        if app_settings.QUERY_EMAIL:
            scope.append('r_emailaddress')
        return scope

    def extract_common_fields(self, data):
        return dict(
            first_name=_extract_name_field(data, 'firstName'),
            last_name=_extract_name_field(data, 'lastName'),
            email=_extract_email(data))


provider_classes = [LinkedInOAuth2Provider]
