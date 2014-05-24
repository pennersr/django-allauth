from __future__ import absolute_import

from allauth.socialaccount.tests import create_oauth2_tests
from allauth.socialaccount.providers import registry
from allauth.tests import MockedResponse

from .provider import MRUProvider


class MRUTests(create_oauth2_tests(registry.by_id(MRUProvider.id))):

    def get_mocked_response(self, verified_email=True):
        return MockedResponse(200, """
{"response": [ { "uid": "15410773191172635989", "first_name": "Евгений", "last_name": "Маслов", "nick": "maslov", "email": "emaslov@mail.ru", "sex": 0,  "birthday": "15.02.1980",  "has_pic": 1, "pic": "http://avt.appsmail.ru/mail/emaslov/_avatar",  "pic_small": "http://avt.appsmail.ru/mail/emaslov/_avatarsmall",  "pic_big": "http://avt.appsmail.ru/mail/emaslov/_avatarbig", "link": "http://my.mail.ru/mail/emaslov/", "referer_type": "", "referer_id": "", "is_online": 1, "friends_count": 145, "is_verified": 1, "vip" : 0, "app_installed": 1, "location": { "country": { "name": "Россия", "id": "24" }, "city": { "name": "Москва", "id": "25" }, "region": { "name": "Москва", "id": "999999" } } },]}
""")
