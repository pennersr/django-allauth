# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from allauth.socialaccount.tests import OAuthTestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import XingProvider


class XingTests(OAuthTestsMixin, TestCase):
    provider_id = XingProvider.id

    def get_mocked_response(self):
        return [MockedResponse(200, """
{"users":[{"id":"20493333_1cd028","active_email":"raymond.penners@gmail.com",
"badges":[],"birth_date":{"year":null,"month":null,"day":null},
"business_address":{"street":null,"zip_code":null,"city":null,"province":null,
"country":"NL","email":null,"fax":null,"phone":null,"mobile_phone":null},
"display_name":"Raymond Penners","educational_background":
{"primary_school_id":null,"schools":[],"qualifications":[]},
"employment_status":"EMPLOYEE","first_name":"Raymond","gender":"m",
"haves":null,"instant_messaging_accounts":{},"interests":null,"languages":
{"nl":null},"last_name":"Penners","organisation_member":null,
"page_name":"Raymond_Penners",
"permalink":"https://www.xing.com/profile/Raymond_Penners",
"photo_urls":{"thumb":"https://www.xing.com/img/n/nobody_m.30x40.jpg",
"large":"https://www.xing.com/img/n/nobody_m.140x185.jpg","mini_thumb":
"https://www.xing.com/img/n/nobody_m.18x24.jpg","maxi_thumb":
"https://www.xing.com/img/n/nobody_m.70x93.jpg","medium_thumb":
"https://www.xing.com/img/n/nobody_m.57x75.jpg"},"premium_services":[],
"private_address":{"street":null,"zip_code":null,"city":null,"province":null,
"country":null,"email":"raymond.penners@gmail.com","fax":null,
"phone":null,"mobile_phone":null},"professional_experience":
{"primary_company":{"name":null,"url":null,"tag":null,"title":null,
"begin_date":null,"end_date":null,"description":null,"industry":"OTHERS",
"company_size":null,"career_level":null},"non_primary_companies":[],
"awards":[]},"time_zone":{"utc_offset":2.0,"name":"Europe/Berlin"},
"wants":null,"web_profiles":{}}]}

""")]
