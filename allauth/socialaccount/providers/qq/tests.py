from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import QQProvider


class QQTests(OAuth2TestsMixin, TestCase):
    provider_id = QQProvider.id

    def get_mocked_response(self):
        return MockedResponse(200, """
{"ret": 0, "msg": "", "is_lost": 0, "nickname": "wow", "gender": "\u7537", "province": "\u6d59\u6c5f", "city": "\u91d1\u534e", "year": "1994", "constellation": "", "figureurl": "http://qzapp.qlogo.cn/qzapp/101491013/D330F1C8BD8B299B933E5FFB973F4AA6/30", "figureurl_1": "http://qzapp.qlogo.cn/qzapp/101491013/D330F1C8BD8B299B933E5FFB973F4AA6/50", "figureurl_2": "http://qzapp.qlogo.cn/qzapp/101491013/D330F1C8BD8B299B933E5FFB973F4AA6/100", "figureurl_qq_1": "http://thirdqq.qlogo.cn/qqapp/101491013/D330F1C8BD8B299B933E5FFB973F4AA6/40", "figureurl_qq_2": "http://thirdqq.qlogo.cn/qqapp/101491013/D330F1C8BD8B299B933E5FFB973F4AA6/100", "is_yellow_vip": "0", "vip": "0", "yellow_vip_level": "0", "level": "0", "is_yellow_year_vip": "0", "openid": "D330F1C8BD8B299B933E5FFB973F4AA6"}

""")
