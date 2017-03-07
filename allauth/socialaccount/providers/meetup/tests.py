from allauth.socialaccount.providers import registry
from allauth.socialaccount.tests import create_oauth2_tests
from allauth.tests import MockedResponse

from .provider import MeetupProvider


class MeetupTests(create_oauth2_tests(
        registry.by_id(MeetupProvider.id))):

    def get_mocked_response(self):
        return MockedResponse(200, """
        {u'lang': u'en_US', u'city': u'Bhubaneswar',
        u'photo': {
        u'thumb_link': 
        u'photo_id': 240057062,
        u'highres_link':
        u'base_url': u'http://photos2.meetupstatic.com',
        u'type': u'member',
        u'name': u'Abhishek Jaiswal', u'other_services': {},
        u'country': u'in', u'topics': [{u'name': u'Open Source',
        u'urlkey': u'opensource', u'id': 563}, {u'name': u'Python', u'urlkey':
        u'python', u'id': 1064}, {u'name': u'Software Development', u'urlkey':
        u'softwaredev', u'id': 3833}, {u'name': u'Computer programming',
        u'urlkey': u'computer-programming', u'id': 48471},
        {u'name': u'Python Web Development', 
        u'urlkey': u'python-web-development', u'id': 917242},
        {u'name': u'Data Science using Python', 
        u'urlkey': u'data-science-using-python', u'id': 1481522}], 
        u'lon': 85.83999633789062, u'joined': 1411642310000, 
        u'id': 173662372, u'status': u'active', 
        u'link': u'http://www.meetup.com/members/173662372', 
        u'hometown': u'Kolkata', u'lat': 20.270000457763672,
        u'visited': 1488829924000, u'self': {u'common': {}}}""")
