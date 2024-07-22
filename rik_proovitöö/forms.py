from django import forms
from django.utils.translation import gettext_lazy as _


class LegalEntitySearchForm(forms.Form):
    query = forms.CharField(label=_('Query'), min_length=3, required=True)
