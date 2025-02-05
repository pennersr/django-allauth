from django.test import TestCase

from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse

from .provider import MailRuProvider


class MailRuTests(OAuth2TestsMixin, TestCase):
    provider_id = MailRuProvider.id

    def get_mocked_response(self, verified_email=True):
        return MockedResponse(
            200,
            """
[ { "uid": "15410773191172635989", "first_name": "Евгений", "last_name": "Маслов", "nick": "maslov", "email": "emaslov@mail.ru", "sex": 0,  "birthday": "15.02.1980",  "has_pic": 1, "pic": "http://avt.appsmail.ru/mail/emaslov/_avatar",  "pic_small": "http://avt.appsmail.ru/mail/emaslov/_avatarsmall",  "pic_big": "http://avt.appsmail.ru/mail/emaslov/_avatarbig", "link": "http://my.mail.ru/mail/emaslov/", "referer_type": "", "referer_id": "", "is_online": 1, "friends_count": 145, "is_verified": 1, "vip" : 0, "app_installed": 1, "location": { "country": { "name": "Россия", "id": "24" }, "city": { "name": "Москва", "id": "25" }, "region": { "name": "Москва", "id": "999999" } } }]""",
        )  # noqa

    def get_login_response_json(self, with_refresh_token=True):
        # TODO: This is not an actual response. I added this in order
        # to get the test suite going but did not verify to check the
        # exact response being returned.
        return '{"access_token": "testac", "uid": "weibo", "refresh_token": "testrf", "x_mailru_vid": "1"}'  # noqa

    def get_expected_to_str(self):
        return "emaslov@mail.ru"
