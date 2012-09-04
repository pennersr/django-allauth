from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin


# Set the domain and name of the example site to be local so that the
# links we generate in confirmation emails can be clicked.
from django.contrib.sites.models import Site
current_site = Site.objects.get_current()
current_site.domain = '127.0.0.1:8000'
current_site.name = 'localhost'
current_site.save()


admin.autodiscover()

urlpatterns = patterns('',
                       (r'^accounts/', include('allauth.urls')),
                       url(r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'index.html' }),
                       url(r'^accounts/profile/$', 'django.views.generic.simple.direct_to_template', {'template': 'profile.html' }),
                       url(r'^admin/', include(admin.site.urls)),
)
