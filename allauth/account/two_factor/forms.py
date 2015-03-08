from binascii import unhexlify
from time import time

from django import forms

from django_otp.oath import totp
from django_otp.plugins.otp_totp.models import TOTPDevice

from django.utils.translation import ugettext_lazy as _


class TOTPDeviceForm(forms.Form):
    token = forms.CharField(
        label=_("Token"),
    )

    def __init__(self, key, user, metadata=None, **kwargs):
        super(TOTPDeviceForm, self).__init__(**kwargs)
        self.key = key
        self.tolerance = 1
        self.t0 = 0
        self.step = 30
        self.drift = 0
        self.digits = 6
        self.user = user
        self.metadata = metadata or {}

    def clean_token(self):
        token = int(self.cleaned_data.get('token'))
        valid = False
        t0s = [self.t0]
        key = unhexlify(self.key.encode())
        if 'valid_t0' in self.metadata:
            t0s.append(int(time()) - self.metadata['valid_t0'])
        for t0 in t0s:
            for offset in range(-self.tolerance, self.tolerance):
                expected_token = totp(
                    key,
                    self.step,
                    t0,
                    self.digits,
                    self.drift + offset
                )

                if expected_token == token:
                    self.drift = offset
                    self.metadata['valid_t0'] = int(time()) - t0
                    valid = True

        if not valid:
            raise forms.ValidationError(_('The entered token is not valid'))
        return token

    def save(self):
        return TOTPDevice.objects.create(
            user=self.user,
            key=self.key,
            tolerance=self.tolerance,
            t0=self.t0,
            step=self.step,
            drift=self.drift,
            digits=self.digits,
            name='default'
        )

