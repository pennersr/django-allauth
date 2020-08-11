from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import ZoomProvider


class ZoomTests(OAuth2TestsMixin, TestCase):
    provider_id = ZoomProvider.id

    def get_mocked_response(self):
        return MockedResponse(200, """
{
  "id": "KdYKjnimT4KPd8FFgQt9FQ",
  "first_name": "Jane",
  "last_name": "Dev",
  "email": "jane.dev@email.com",
  "type": 2,
  "role_name": "Owner",
  "pmi": 1234567890,
  "use_pmi": false,
  "vanity_url": "https://janedevinc.zoom.us/my/janedev",
  "personal_meeting_url": "https://janedevinc.zoom.us/j/1234567890",
  "timezone": "America/Denver",
  "verified": 1,
  "dept": "",
  "created_at": "2019-04-05T15:24:32Z",
  "last_login_time": "2019-12-16T18:02:48Z",
  "last_client_version": "4.6.12611.1124(mac)",
  "pic_url": "https://janedev.zoom.us/p/KdYKjnimFR5Td8KKdQt9FQ/19f6430f-...",
  "host_key": "533895",
  "jid": "kdykjnimt4kpd8kkdqt9fq@xmpp.zoom.us",
  "group_ids": [],
  "im_group_ids": [
    "3NXCD9VFTCOUH8LD-QciGw"
  ],
  "account_id": "gVcjZnYYRLDbb_MfgHuaxg",
  "language": "en-US",
  "phone_country": "US",
  "phone_number": "+1 1234567891",
  "status": "active"
}
""")
