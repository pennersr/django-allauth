from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import YahooProvider


class YahooTests(OAuth2TestsMixin, TestCase):
    provider_id = YahooProvider.id

    def get_mocked_response(self):
        response_data = """
        {
            "profile": {
                "guid": "HZP2G4VBSQBVATWWTNO3CRKVP8",
                "addresses": [
                    {
                        "city": "Timbuktu",
                        "country": "US",
                        "current": true,
                        "id": 1,
                        "postalCode": "100013",
                        "state": "New York",
                        "street": "",
                        "type": "HOME"
                    },
                    {
                        "city": "",
                        "country": "US",
                        "current": true,
                        "id": 2,
                        "postalCode": "",
                        "state": "",
                        "street": "",
                        "type": "WORK"
                    }
                ],
                "ageCategory": "A",
                "birthYear": 1982,
                "birthdate": "2/15",
                "created": "2017-09-09T13:45:29Z",
                "displayAge": 28,
                "emails": [
                    {
                        "handle": "john.doe@yahoo.com",
                        "id": 2,
                        "primary": false,
                        "type": "HOME"
                    }
                ],
                "familyName": "Doe",
                "gender": "M",
                "givenName": "John",
                "image": {
                    "height": 192,
                    "imageUrl": "https://s.yimg.com/wm/modern/images/default_user_profile_pic_192.png",
                    "size": "192x192",
                    "width": 192
                },
                "ims": [
                    {
                        "handle": "john.doe",
                        "id": 1,
                        "type": "YAHOO"
                    }
                ],
                "intl": "us",
                "jurisdiction": "us",
                "lang": "en-US",
                "memberSince": "2000-08-18T12:28:31Z",
                "migrationSource": 1,
                "nickname": "john.doe",
                "notStored": true,
                "nux": "0",
                "profileMode": "PUBLIC",
                "profileStatus": "ACTIVE",
                "profileUrl": "http://profile.yahoo.com/HZP2G4VBSQBVATWWTNO3CRKVP8",
                "timeZone": "Asia/Calcutta",
                "isConnected": true,
                "profileHidden": false,
                "profilePermission": "PRIVATE",
                "uri": "https://social.yahooapis.com/v1/user/HZP2G4VBSQBVATWWTNO3CRKVP8/profile"
            }
        }
        """ # noqa
        return MockedResponse(200, response_data)
