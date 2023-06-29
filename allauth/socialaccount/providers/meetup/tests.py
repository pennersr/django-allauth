from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import MeetupProvider


class MeetupTests(OAuth2TestsMixin, TestCase):
    provider_id = MeetupProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
        {"id": 1, "lang": "en_US", "city": "Bhubaneswar",
        "photo": {
        "thumb_link":"",
        "photo_id": 240057062,
        "highres_link":"",
        "base_url": "http://photos2.meetupstatic.com",
        "type": "member",
        "name": "Abhishek Jaiswal", "other_services": {},
        "country": "in", "topics": [{"name": "Open Source",
        "urlkey": "opensource", "id": 563}, {"name": "Python", "urlkey":
        "python", "id": 1064}, {"name": "Software Development", "urlkey":
        "softwaredev", "id": 3833}, {"name": "Computer programming",
        "urlkey": "computer-programming", "id": 48471},
        {"name": "Python Web Development",
        "urlkey": "python-web-development", "id": 917242},
        {"name": "Data Science using Python",
        "urlkey": "data-science-using-python", "id": 1481522}],
        "lon": 85.83999633789062, "joined": 1411642310000,
        "id": 173662372, "status": "active",
        "link": "http://www.meetup.com/members/173662372",
        "hometown": "Kolkata", "lat": 20.270000457763672,
        "visited": 1488829924000, "self": {"common": {}}}}""",
        )
