from django.urls import include, path, re_path

from . import views


urlpatterns = [
    re_path(
        r"^saml/(?P<organization_slug>[^/]+)/",
        include(
            [
                path(
                    "acs/",
                    views.acs,
                    name="saml_acs",
                ),
                path(
                    "acs/finish/",
                    views.finish_acs,
                    name="saml_finish_acs",
                ),
                path(
                    "sls/",
                    views.sls,
                    name="saml_sls",
                ),
                path(
                    "metadata/",
                    views.metadata,
                    name="saml_metadata",
                ),
                path(
                    "login/",
                    views.login,
                    name="saml_login",
                ),
            ]
        ),
    )
]
