from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import TemplateView
admin.autodiscover()

urlpatterns = patterns('',
                       (r'^accounts/', include('allauth.urls')),
                       url(r'^$', TemplateView.as_view(template_name='index.html')),
                       url(r'^accounts/profile/$', TemplateView.as_view(template_name='profile.html')),
                       url(r'^admin/', include(admin.site.urls)),
)
