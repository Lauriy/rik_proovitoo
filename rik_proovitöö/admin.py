from datetime import date

from django.conf import settings
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory, ModelForm
from django.utils.translation import gettext_lazy as _

from rik_proovitöö.models import LegalEntity, Equity


# TODO: Move to utils?
def _calculate_personal_check_digit(personal_code: int) -> int:
    personal_code = str(personal_code)
    first_tier_weights = [1, 2, 3, 4, 5, 6, 7, 8, 9, 1]
    second_tier_weights = [3, 4, 5, 6, 7, 8, 9, 1, 2, 3]
    first_tier_weight_sum = sum(
        [
            int(x) * first_tier_weights[i]
            for i, x in enumerate(personal_code[:10])
        ]
    )
    possible_check_digit = first_tier_weight_sum % 11
    if possible_check_digit != 10:
        return possible_check_digit
    else:
        second_tier_weight_sum = sum(
            [
                int(x) * second_tier_weights[i]
                for i, x in enumerate(personal_code[:10])
            ]
        )
        possible_check_digit = second_tier_weight_sum % 11
        if possible_check_digit != 10:
            return possible_check_digit
        else:
            return 0


def _calculate_birth_year(personal_code: int) -> int:
    personal_code = str(personal_code)
    if personal_code[0] in ["1", "2"]:
        year_digits = "18"
    elif personal_code[0] in ["3", "4"]:
        year_digits = "19"
    else:
        year_digits = "20"

    return int(f"{year_digits}{personal_code[1:3]}")


def _convert_to_birthdate(personal_code: int) -> date:
    birth_year = _calculate_birth_year(personal_code)
    personal_code = str(personal_code)
    birth_month = int(personal_code[3:5])
    birth_day = int(personal_code[5:7])

    return date(year=birth_year, month=birth_month, day=birth_day)


class EquityInline(admin.TabularInline):
    model = Equity
    fk_name = 'company'
    extra = 1


class LegalEntityForm(ModelForm):
    class Meta:
        model = LegalEntity
        fields = ['name', 'code', 'creation_date', 'capital', 'is_person']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['capital'].required = False
        self.fields['creation_date'].required = False

    def clean(self):
        cleaned_data = super().clean()
        is_person = cleaned_data.get('is_person')
        code = cleaned_data.get('code')
        creation_date = cleaned_data.get('creation_date')
        capital = cleaned_data.get('capital')

        if is_person:
            if len(str(code)) != 11:
                raise ValidationError(_('Personal codes must be 11 digits long'))
            is_check_digit_correct = _calculate_personal_check_digit(code) == int(str(code)[-1])
            if not is_check_digit_correct:
                raise ValidationError(_('Personal code check digit is incorrect'))
            cleaned_data['creation_date'] = _convert_to_birthdate(code)
            cleaned_data['capital'] = None
        else:
            if len(str(code)) != 7:
                raise ValidationError(_('Business codes must be 7 digits long'))
            if not creation_date:
                raise ValidationError(_('Businesses must have an establishment date specified'))
            if not capital or capital < settings.LLC_MIN_CAPITAL:
                raise ValidationError(_('Businesses must have at least %(min_capital)s capital') % {
                    'min_capital': settings.LLC_MIN_CAPITAL})

        return cleaned_data


EquityFormSet = inlineformset_factory(
    LegalEntity,
    Equity,
    fk_name='company',
    fields=('stakeholder', 'value', 'is_founding'),
    extra=1
)


class LegalEntityAdmin(admin.ModelAdmin):
    form = LegalEntityForm
    inlines = [EquityInline]

    def get_fieldsets(self, request, obj=None):
        if obj and obj.is_person:
            return (
                (None, {'fields': ('name', 'code', 'is_person')}),
            )
        return (
            (None, {'fields': ('name', 'code', 'creation_date', 'capital', 'is_person')}),
        )

    def get_inline_instances(self, request, obj=None):
        if obj is None or not obj.is_person:
            return super().get_inline_instances(request, obj)

        return []

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        if not form.instance.is_person:
            total_equity = sum(equity.value for equity in form.instance.stakes.all())
            if total_equity != form.instance.capital:
                raise ValidationError(
                    _('Total equity holdings (%(total_equity)s) do not match the company\'s capital (%(capital)s)') % {
                        'total_equity': total_equity, 'capital': form.instance.capital}
                )


admin.site.register(LegalEntity, LegalEntityAdmin)
admin.site.register(Equity)
