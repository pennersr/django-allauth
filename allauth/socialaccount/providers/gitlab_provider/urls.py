# -*- coding: utf-8 -*-
from allauth.socialaccount.providers.gitlab_provider.provider import GitLabProvider
from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns


urlpatterns = default_urlpatterns(GitLabProvider)
