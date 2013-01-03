from django.test import TestCase
from datetime import datetime
from allauth.socialaccount.providers.stackexchange.models import StackExchangeSite
from django.utils.timezone import utc
#from allauth.socialaccount.models import SocialApp
#from stackpy.api import API

class StackExchangeSiteModelTest(TestCase):
    def test_creating_new_stackexchangesite_and_saving_it_to_database(self):
        sesite = StackExchangeSite()

        # Mandatory fields
        sesite.api_site_parameter = 'stackoverflow'
        sesite.audience = 'professional and enthusiast programmers'
        sesite.favicon_url = 'http://cdn.sstatic.net/stackoverflow/img/favicon.ico'
        sesite.icon_url = 'http://cdn.sstatic.net/stackoverflow/img/apple-touch-icon.png'
        sesite.launch_date = datetime.utcfromtimestamp(1221436800).replace(tzinfo=utc)
        sesite.logo_url = 'http://cdn.sstatic.net/stackoverflow/img/logo.png'
        sesite.name = 'Stack Overflow'
        sesite.site_state = 'normal'
        sesite.site_type = 'main_site'
        sesite.site_url = 'http://stackoverflow.com'
        sesite.styling_link_color = '#0077CC'
        sesite.styling_tag_foreground_color = '#3E6D8E'
        sesite.styling_tag_background_color = '#E0EAF1'

        # Save it
        sesite.save()

        # Now see if we can get it back
        all_stackexchange_sites_in_database = StackExchangeSite.objects.all()
        self.assertEquals(len(all_stackexchange_sites_in_database), 1)
        only_stackexchange_site_in_database = all_stackexchange_sites_in_database[0]
        self.assertEquals(only_stackexchange_site_in_database, sesite)

        # Check if all attributes are saved properly
        self.assertEquals(sesite.api_site_parameter, only_stackexchange_site_in_database.api_site_parameter)
        self.assertEquals(sesite.audience, only_stackexchange_site_in_database.audience)
        self.assertEquals(sesite.favicon_url, only_stackexchange_site_in_database.favicon_url)
        self.assertEquals(sesite.icon_url, only_stackexchange_site_in_database.icon_url)
        self.assertEquals(sesite.launch_date, only_stackexchange_site_in_database.launch_date)
        self.assertEquals(sesite.logo_url, only_stackexchange_site_in_database.logo_url)
        self.assertEquals(sesite.name, only_stackexchange_site_in_database.name)
        self.assertEquals(sesite.site_state, only_stackexchange_site_in_database.site_state)
        self.assertEquals(sesite.site_type, only_stackexchange_site_in_database.site_type)
        self.assertEquals(sesite.site_url, only_stackexchange_site_in_database.site_url)
        self.assertEquals(sesite.styling_link_color, only_stackexchange_site_in_database.styling_link_color)
        self.assertEquals(sesite.styling_tag_foreground_color, only_stackexchange_site_in_database.styling_tag_foreground_color)
        self.assertEquals(sesite.styling_tag_background_color, only_stackexchange_site_in_database.styling_tag_background_color)
