from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import NaverProvider


class NaverTests(OAuth2TestsMixin, TestCase):
    provider_id = NaverProvider.id

    def get_mocked_response(self):
        return MockedResponse(200, """
{
"response":
{
"enc_id": "46111c25f969116de4e545f13a415bb5383db2a79782da8851db72b2cced3180",
"nickname": "\ubc31\ud638",
"profile_image":
"https://ssl.pstatic.net/static/pwe/address/nodata_33x33.gif",
"gender": "M",
"id": "7163491",
"age": "20-29",
"birthday": "03-22",
"email": "shlee940322@naver.com",
"name": "\uc774\uc0c1\ud601"
},
"message": "success",
"resultcode": "00"
}
""")
