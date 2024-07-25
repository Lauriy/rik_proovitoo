from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from rik_proovitöö.forms import LegalEntityForm
from rik_proovitöö.models import LegalEntity, Equity


class EquityInline(admin.TabularInline):
    model = Equity
    fk_name = 'company'
    extra = 1


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
            total_equity = 0
            for formset in formsets:
                for equity_form in formset.forms:
                    if equity_form.is_valid() and equity_form not in formset.deleted_forms:
                        total_equity += equity_form.cleaned_data.get('value', 0)

            capital = form.cleaned_data.get('capital', 0)
            if total_equity != capital:
                raise ValidationError(
                    _('Total equity holdings (%(total_equity)s) do not match the company\'s capital (%(capital)s)') % {
                        'total_equity': total_equity, 'capital': capital}
                )


admin.site.register(LegalEntity, LegalEntityAdmin)
admin.site.register(Equity)
