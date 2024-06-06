from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import FoursquareProvider


class FoursquareTests(OAuth2TestsMixin, TestCase):
    provider_id = FoursquareProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
{"notifications": [{"item": {"unreadCount": 0}, "type": "notificationTray"}],
                                "meta": {"code": 200},
 "response": {
 "user": {
   "photo": {
     "prefix": "https://irs0.4sqi.net/img/user/", "suffix": "/blank_boy.png"},
   "pings": false,
   "homeCity": "Athens, ESYE31",
   "id": "76077726",
   "badges": {"count": 0, "items": []},
   "referralId": "u-76077726",
   "friends":
   {
       "count": 0,
       "groups": [{"count": 0, "items": [], "type": "friends",
"name": "Mutual friends"}, {"count": 0, "items": [], "type": "others",
"name": "Other friends"}]
   },
   "createdAt": 1389624445,
   "tips": {"count": 0},
   "type": "user",
   "bio": "",
   "relationship": "self",
   "lists":
   {
       "count": 1,
       "groups": [{"count": 1, "items": [{"description": "",
"collaborative": false, "url": "/user/76077726/list/todos", "editable": false,
"listItems": {"count": 0}, "id": "76077726/todos", "followers": {"count": 0},
"user": {"gender": "male",
"firstName": "\u03a1\u03c9\u03bc\u03b1\u03bd\u03cc\u03c2",
"relationship": "self", "photo": {"prefix": "https://irs0.4sqi.net/img/user/",
"suffix": "/blank_boy.png"},
"lastName": "\u03a4\u03c3\u03bf\u03c5\u03c1\u03bf\u03c0\u03bb\u03ae\u03c2",
"id": "76077726"}, "public": false,
"canonicalUrl": "https://foursquare.com/user/76077726/list/todos",
"name": "My to-do list"}], "type": "created"}, {"count": 0, "items": [],
"type": "followed"}]
   },
   "photos": {"count": 0, "items": []},
   "checkinPings": "off",
   "scores": {"max": 0, "checkinsCount": 0, "goal": 50, "recent": 0},
   "checkins": {"count": 0, "items": []},
   "firstName": "\u03a1\u03c9\u03bc\u03b1\u03bd\u03cc\u03c2",
   "gender": "male",
   "contact": {"email": "romdimtsouroplis@example.com"},
   "lastName": "\u03a4\u03c3\u03bf\u03c5\u03c1\u03bf\u03c0\u03bb\u03ae\u03c2",
   "following": {"count": 0, "groups": [{"count": 0, "items": [],
"type": "following", "name": "Mutual following"}, {"count": 0, "items": [],
"type": "others", "name": "Other following"}]},
   "requests": {"count": 0}, "mayorships": {"count": 0, "items": []}}
                                    }
                                 }
""",
        )
