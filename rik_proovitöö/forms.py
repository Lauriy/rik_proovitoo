from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms import Form, CharField, ModelForm, inlineformset_factory, DateInput
from django.utils.translation import gettext_lazy as _

from rik_proovitöö.models import LegalEntity, Equity
from rik_proovitöö.utils import calculate_personal_check_digit, convert_to_birthdate


class LegalEntitySearchForm(Form):
    query = CharField(label=_('Query'), min_length=3, required=True)


class LegalEntityForm(ModelForm):
    class Meta:
        model = LegalEntity
        fields = ['name', 'code', 'creation_date', 'capital', 'is_person']
        labels = {
            'name': _('Name'),
            'code': _('Code'),
            'creation_date': _('Creation date'),
            'capital': _('Capital'),
            'is_person': _('Is person'),
        }

    def __init__(self, *args, **kwargs):
        exclude_is_person = kwargs.pop('exclude_is_person', False)
        super().__init__(*args, **kwargs)
        if exclude_is_person:
            self.fields.pop('is_person', None)
        self.fields['capital'].required = False
        self.fields['creation_date'].required = False
        self.fields['creation_date'].widget = DateInput(attrs={'type': 'date'})

    def clean(self):
        cleaned_data = super().clean()
        is_person = cleaned_data.get('is_person')
        code = cleaned_data.get('code')
        creation_date = cleaned_data.get('creation_date')
        capital = cleaned_data.get('capital')

        if is_person:
            if len(str(code)) != 11:
                raise ValidationError(_('Personal codes must be 11 digits long'))
            is_check_digit_correct = calculate_personal_check_digit(code) == int(str(code)[-1])
            if not is_check_digit_correct:
                raise ValidationError(_('Personal code check digit is incorrect'))
            cleaned_data['creation_date'] = convert_to_birthdate(code)
            cleaned_data['capital'] = None
        else:
            if len(str(code)) != 7:
                raise ValidationError(_('Business codes must be 7 digits long'))
            if not creation_date:
                raise ValidationError(_('Businesses must have an establishment date specified'))
            if not capital or capital < settings.LLC_MIN_CAPITAL:
                raise ValidationError(_('Businesses must have at least %(min_capital)s capital') % {
                    'min_capital': settings.LLC_MIN_CAPITAL})
            total_equity = sum(form.cleaned_data.get('value', 0) for form in self.equity_formset.forms if
                               form not in self.equity_formset.deleted_forms)
            if total_equity != capital:
                raise ValidationError(
                    _('Total equity holdings (%(total_equity)s) do not match the company\'s capital (%(capital)s)') % {
                        'total_equity': total_equity, 'capital': capital})

        return cleaned_data


class EquityForm(ModelForm):
    class Meta:
        model = Equity
        fields = ('stakeholder', 'value', 'is_founding')
        labels = {
            'stakeholder': _('Stakeholder'),
            'value': _('Value'),
            'is_founding': _('Is founding'),
        }


class PublicEquityForm(ModelForm):
    class Meta:
        model = Equity
        fields = ('stakeholder', 'value', 'id')
        labels = {
            'stakeholder': _('Stakeholder'),
            'value': _('Value'),
        }


AdminEquityFormSet = inlineformset_factory(
    LegalEntity,
    Equity,
    form=EquityForm,
    fk_name='company',
    fields=('stakeholder', 'value', 'is_founding'),
    extra=1,
    can_delete=True
)

PublicEquityFormSet = inlineformset_factory(
    LegalEntity,
    Equity,
    form=PublicEquityForm,
    fk_name='company',
    fields=('id', 'stakeholder', 'value'),
    extra=1,
    can_delete=True
)
