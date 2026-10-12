from __future__ import annotations

from hashlib import md5

from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.utils.http import urlencode

from allauth.socialaccount.providers.base import Provider, ProviderAccount


AUTHORIZE_URL = "https://api.draugiem.lv/authorize"


class DraugiemAccount(ProviderAccount):
    def get_avatar_url(self):
        ret = None
        pic_small_url = self.account.extra_data.get("img")
        pic_icon_url = self.account.extra_data.get("imgi")
        pic_medium_url = self.account.extra_data.get("imgm")
        pic_large_url = self.account.extra_data.get("imgl")
        if pic_large_url:
            return pic_large_url
        elif pic_medium_url:
            return pic_medium_url
        elif pic_icon_url:
            return pic_icon_url
        elif pic_small_url:
            return pic_small_url
        else:
            return ret


class DraugiemProvider(Provider):
    id = "draugiem"
    name = "Draugiem"
    account_class = DraugiemAccount

    def get_login_url(self, request: HttpRequest, **kwargs):
        url = reverse(f"{self.id}_login")
        if kwargs:
            url = f"{url}?{urlencode(kwargs)}"
        return url

    def extract_uid(self, data):
        return str(data["uid"])

    def extract_common_fields(self, data):
        uid = self.extract_uid(data)
        user_data = data["users"][uid]
        return dict(
            first_name=user_data.get("name"),
            last_name=user_data.get("surname"),
        )

    def extract_extra_data(self, data):
        uid = self.extract_uid(data)
        return data["users"][uid]

    def redirect(
        self, request: HttpRequest, process, next_url=None, data=None, **kwargs
    ):
        redirect_url = request.build_absolute_uri(reverse("draugiem_callback"))
        app = self.app
        # Draugiem mandates a weak hashing algorithm.
        redirect_url_hash = md5(
            f"{app.secret}{redirect_url}".encode()
        ).hexdigest()  # nosec
        params = {
            "app": app.client_id,
            "hash": redirect_url_hash,
            "redirect": redirect_url,
        }
        self.stash_redirect_state(
            request, process=process, next_url=next_url, data=data, **kwargs
        )
        return HttpResponseRedirect(f"{AUTHORIZE_URL}?{urlencode(params)}")


provider_classes = [DraugiemProvider]
