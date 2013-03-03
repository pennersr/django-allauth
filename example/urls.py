try:
    from django.conf.urls import patterns, url, include
except ImportError:
    # for Django version less then 1.4
    from django.conf.urls.defaults import patterns, url, include
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
                       (r'^accounts/', include('allauth.urls')),
                       url(r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'index.html' }),
                       url(r'^accounts/profile/$', 'django.views.generic.simple.direct_to_template', {'template': 'profile.html' }),
                       url(r'^admin/', include(admin.site.urls)),
)
