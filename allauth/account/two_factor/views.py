
from base64 import b32encode
from binascii import unhexlify
from django.contrib.auth.models import User
from django_otp.plugins.otp_static.models import StaticToken

try:
    from urllib.parse import quote, urlencode
except ImportError:
    from urllib import quote, urlencode

from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic import FormView, View, TemplateView
from django_otp.util import random_hex
from django.contrib.sites.models import get_current_site
from django.http import HttpResponse

from allauth.account.two_factor.forms import (
    TOTPDeviceForm,
    TOTPAuthenticateForm,
)

import qrcode
from qrcode.image.svg import SvgPathImage


class TwoFactorAuthenticate(FormView):
    template_name = 'account/two_factor/authenticate.html'
    form_class = TOTPAuthenticateForm
    success_url = reverse_lazy('profile')

    def get_form_kwargs(self):
        kwargs = super(TwoFactorAuthenticate, self).get_form_kwargs()
        user_id = self.request.session['user_id']
        kwargs['user'] = User.objects.get(id=user_id)
        return kwargs

    def form_valid(self, form):
        from django.contrib.auth import login
        if not hasattr(form.user, 'backend'):
            form.user.backend \
                = "allauth.account.auth_backends.AuthenticationBackend"
        login(self.request, form.user)
        return super(TwoFactorAuthenticate, self).form_valid(form)

two_factor_authenticate = TwoFactorAuthenticate.as_view()


class TwoFactorSetup(FormView):
    template_name = 'account/two_factor/setup.html'
    form_class = TOTPDeviceForm
    success_url = reverse_lazy('profile')

    def dispatch(self, request, *args, **kwargs):

        if 'allauth_otp_qr_secret_key' not in request.session:
            self.secret_key = random_hex(20).decode('ascii')
            request.session['allauth_otp_qr_secret_key'] = self.secret_key
        else:
            self.secret_key = request.session['allauth_otp_qr_secret_key']

        if request.user.totpdevice_set.exists():
            return HttpResponseRedirect(reverse_lazy('profile'))
        return super(TwoFactorSetup, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(TwoFactorSetup, self).get_form_kwargs()
        kwargs['key'] = self.secret_key
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        return super(TwoFactorSetup, self).form_valid(form)

two_factor_setup = TwoFactorSetup.as_view()


class TwoFactorBackupTokens(TemplateView):
    template_name = 'account/two_factor/backup_tokens.html'

    def get_context_data(self, **kwargs):
        context = super(TwoFactorBackupTokens, self).get_context_data(*kwargs)
        static_device, _ = self.request.user.staticdevice_set.get_or_create(
            name='backup'
        )

        if static_device:
            context['backup_tokens'] = static_device.token_set.all()

        return context

    def post(self, request, *args, **kwargs):
        static_device, _ = request.user.staticdevice_set.get_or_create(
            name='backup'
        )
        static_device.token_set.all().delete()
        for _ in range(10):
            static_device.token_set.create(token=StaticToken.random_token())
        return self.get(request, *args, **kwargs)


two_factor_backup_tokens = TwoFactorBackupTokens.as_view()


class QRCodeGeneratorView(View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        content_type = 'image/svg+xml; charset=utf-8'
        raw_key = request.session['allauth_otp_qr_secret_key']
        secret_key = b32encode(unhexlify(raw_key)).decode('utf-8')

        otpauth_url = 'otpauth://totp/{label}?{query}'.format(
            label=quote('{issuer}: {username}'.format(
                issuer=get_current_site(request).name,
                username=request.user.username
            )),
            query=urlencode({
                'secret': secret_key,
                'digits': 6,
                'issuer': get_current_site(request).name
            })
        )

        img = qrcode.make(otpauth_url, image_factory=SvgPathImage)
        response = HttpResponse(content_type=content_type)
        img.save(response)
        return response
two_factor_qr_code_generator = QRCodeGeneratorView.as_view()
