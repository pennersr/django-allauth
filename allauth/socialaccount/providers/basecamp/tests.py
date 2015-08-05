from allauth.socialaccount.tests import create_oauth2_tests
from allauth.tests import MockedResponse
from allauth.socialaccount.providers import registry

from .provider import BasecampProvider


class BasecampTests(create_oauth2_tests(registry.by_id(BasecampProvider.id))):
    def get_mocked_response(self):
        return MockedResponse(200, """
        {
          "id": 149087659,
          "identity_id": 982871737,
          "name": "Jason Fried",
          "email_address": "jason@basecamp.com",
          "admin": true,
          "trashed": false,
          "avatar_url": "https://asset0.37img.com/global/4113d0a133a32931be8934e70b2ea21efeff72c1/avatar.96.gif?r=3",
          "fullsize_avatar_url": "https://asset0.37img.com/global/4113d0a133a32931be8934e70b2ea21efeff72c1/original.gif?r=3",
          "created_at": "2012-03-22T16:56:51-05:00",
          "updated_at": "2012-03-23T13:55:43-05:00",
          "events": {
            "count": 19,
            "updated_at": "2012-03-23T13:55:43-05:00",
            "url": "https://basecamp.com/999999999/api/v1/people/149087659-jason-fried/events.json",
            "app_url": "https://basecamp.com/999999999/people/149087659-jason-fried/events"
          },
          "assigned_todos": {
            "count": 80,
            "updated_at": "2013-06-26T16:22:05.000-04:00",
            "url": "https://basecamp.com/999999999/api/v1/people/149087659-jason-fried/assigned_todos.json",
            "app_url": "https://basecamp.com/999999999/people/149087659-jason-fried/assigned_todos"
          }
        }""")
