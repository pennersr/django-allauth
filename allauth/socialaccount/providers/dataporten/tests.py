from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import DataportenProvider


class DataportenTest(OAuth2TestsMixin, TestCase):
    provider_id = DataportenProvider.id

    def setUp(self):
        super(DataportenTest, self).setUp()
        self.mock_data = {
            'userid': '76a7a061-3c55-430d-8ee0-6f82ec42501f',
            'userid_sec': ['feide:andreas@uninett.no'],
            'name': 'Andreas \u00c5kre Solberg',
            'email': 'andreas.solberg@uninett.no',
            'profilephoto': 'p:a3019954-902f-45a3-b4ee-bca7b48ab507',
            'groups': [{}],
        }

    def get_login_response_json(self, with_refresh_token=True):
        rt = ''
        if with_refresh_token:
            rt = ',"refresh_token": "testrf"'
        return '''{
            "access_token":"testac",
            "expires_in":3600,
            "scope": "userid profile groups"
            %s
        }''' % rt

    def get_mocked_response(self):
        return MockedResponse(
            status_code=200,
            content='''{
                "user": {
                    "userid": "76a7a061-3c55-430d-8ee0-6f82ec42501f",
                    "userid_sec": ["feide:andreas@uninett.no"],
                    "name": "Andreas \u00c5kre Solberg",
                    "email": "andreas.solberg@uninett.no",
                    "profilephoto": "p:a3019954-902f-45a3-b4ee-bca7b48ab507"
                },
                "audience": "app123id"
            }''',
            headers={'content-type': 'application/json'},
            )

    def test_extract_uid(self):
        uid = self.provider.extract_uid(self.mock_data)
        self.assertEqual(uid, self.mock_data['userid'])

    def test_extract_extra_data(self):
        # All the processing is done in the complete_login view, and thus
        # the data should be returned unaltered
        extra_data = self.provider.extract_extra_data(self.mock_data)
        self.assertEqual(extra_data, self.mock_data)

    def test_extract_common_fields(self):
        # The main task of this function is to parse the data in order to
        # find the Feide username, and if not, use the email
        common_fields = self.provider.extract_common_fields(self.mock_data)
        self.assertEqual(common_fields['username'], 'andreas')

        # Test correct behaviour when Feide username is unavailable
        new_mock_data = dict(self.mock_data)
        new_mock_data['userid_sec'] = []
        new_common_fields = self.provider.extract_common_fields(new_mock_data)
        self.assertEqual(new_common_fields['username'], 'andreas.solberg')
