# -*- coding: utf-8 -*-
from allauth.socialaccount.providers.gitlab.provider import GitLabProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(GitLabProvider)
