from django.urls import include, path

from allauth.headless.socialaccount import views


urlpatterns = [
    path(
        "account/",
        include(
            [
                path(
                    "providers",
                    views.manage_providers,
                    name="headless_manage_providers",
                ),
            ]
        ),
    ),
    path(
        "auth/",
        include(
            [
                path(
                    "provider/",
                    include(
                        [
                            path(
                                "signup",
                                views.provider_signup,
                                name="headless_provider_signup",
                            ),
                            path(
                                "redirect",
                                views.redirect_to_provider,
                                name="headless_redirect_to_provider",
                            ),
                        ]
                    ),
                )
            ]
        ),
    ),
]
