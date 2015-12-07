# -*- coding: utf-8 -*-
from allauth.socialaccount.tests import OAuthTestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import VimeoProvider


class VimeoTests(OAuthTestsMixin, TestCase):
    provider_id = VimeoProvider.id

    def get_mocked_response(self):
        return [MockedResponse(200, """
{"generated_in":"0.0137","stat":"ok","person":{"created_on":"2013-04-08 14:24:47","id":"17574504","is_contact":"0","is_plus":"0","is_pro":"0","is_staff":"0","is_subscribed_to":"0","username":"user17574504","display_name":"Raymond Penners","location":"","url":[""],"bio":"","number_of_contacts":"0","number_of_uploads":"0","number_of_likes":"0","number_of_videos":"0","number_of_videos_appears_in":"0","number_of_albums":"0","number_of_channels":"0","number_of_groups":"0","profileurl":"http:\\/\\/vimeo.com\\/user17574504","videosurl":"http:\\/\\/vimeo.com\\/user17574504\\/videos","portraits":{"portrait":[{"height":"30","width":"30","_content":"http:\\/\\/a.vimeocdn.com\\/images_v6\\/portraits\\/portrait_30_yellow.png"},{"height":"75","width":"75","_content":"http:\\/\\/a.vimeocdn.com\\/images_v6\\/portraits\\/portrait_75_yellow.png"},{"height":"100","width":"100","_content":"http:\\/\\/a.vimeocdn.com\\/images_v6\\/portraits\\/portrait_100_yellow.png"},{"height":"300","width":"300","_content":"http:\\/\\/a.vimeocdn.com\\/images_v6\\/portraits\\/portrait_300_yellow.png"}]}}}
""")]
