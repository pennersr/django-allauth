from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import LichessProvider


class LichessTests(OAuth2TestsMixin, TestCase):
    provider_id = LichessProvider.id

    def get_mocked_response(self):
        return [
            MockedResponse(
                200,
                """
{
  "id": "george",
  "url": "https://lichess.org/@/george",
  "count": {
    "ai": 0,
    "me": 0,
    "all": 0,
    "win": 0,
    "draw": 0,
    "loss": 0,
    "winH": 0,
    "drawH": 0,
    "lossH": 0,
    "rated": 0,
    "import": 0,
    "playing": 0,
    "bookmark": 0
  },
  "perfs": {
    "blitz": {
      "rd": 500,
      "prog": 0,
      "prov": true,
      "games": 0,
      "rating": 1500
    },
    "rapid": {
      "rd": 500,
      "prog": 0,
      "prov": true,
      "games": 0,
      "rating": 1500
    },
    "bullet": {
      "rd": 500,
      "prog": 0,
      "prov": true,
      "games": 0,
      "rating": 1500
    },
    "classical": {
      "rd": 500,
      "prog": 0,
      "prov": true,
      "games": 0,
      "rating": 1500
    },
    "correspondence": {
      "rd": 500,
      "prog": 0,
      "prov": true,
      "games": 0,
      "rating": 1500
    }
  },
  "seenAt": 1713837454330,
  "blocking": false,
  "playTime": {
    "tv": 0,
    "total": 0
  },
  "username": "george",
  "createdAt": 1713837409417,
  "following": false,
  "followable": true,
  "followsYou": false
}
""",
            ),
            MockedResponse(200, """{"email":"george@example.com"}"""),
        ]
