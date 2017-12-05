from django.urls import include, path
from django.contrib import admin
from django.views.generic.base import TemplateView
admin.autodiscover()

urlpatterns = [
    path('accounts/', include('allauth.urls')),
    path('', TemplateView.as_view(template_name='index.html')),
    path('accounts/profile/', TemplateView.as_view(template_name='profile.html')),
    path('admin/', include(admin.site.urls)),
]
