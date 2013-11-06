from django import forms

class WykopConnectForm(forms.Form):
    connectData = forms.CharField(required=True)
