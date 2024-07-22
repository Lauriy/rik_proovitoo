from django.contrib.postgres.indexes import GinIndex
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MinValueValidator, MaxValueValidator
from django.db.models import CharField, Model, DateField, IntegerField, CASCADE, ForeignKey, DateTimeField, \
    BooleanField, Index, BigIntegerField
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class CreatedUpdatedMixin:
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)


def no_future_date(value):
    if value > timezone.now().date():
        raise ValidationError(_('Legal entities cannot be established into the future'))


class LegalEntity(Model, CreatedUpdatedMixin):
    name = CharField(max_length=100, validators=[
        MinLengthValidator(3),
    ])
    code = BigIntegerField(validators=[
        MinValueValidator(1000000),  # 7 digits is the minimum for OÜ-s
        MaxValueValidator(99999999999),  # 11 digits is the maximum for personal codes
    ])
    creation_date = DateField(validators=[no_future_date], null=True, blank=True)
    capital = IntegerField(blank=True, null=True)  # People don't have this
    is_person = BooleanField(default=False)

    def __str__(self):
        return f'{self.name} ({self.code})'

    class Meta:
        verbose_name = _('Legal entity')
        verbose_name_plural = _('Legal entities')
        indexes = [
            Index(fields=['code']),  # Regular index for URL traversal
            GinIndex(fields=['name'], name='gin_trgm_idx', opclasses=['gin_trgm_ops']),  # GinIndex for search
        ]


class Equity(Model, CreatedUpdatedMixin):
    stakeholder = ForeignKey('LegalEntity', on_delete=CASCADE, related_name='holdings')
    company = ForeignKey('LegalEntity', on_delete=CASCADE, related_name='stakes')
    value = IntegerField()
    is_founding = BooleanField(default=True)

    def __str__(self):
        return f'{self.stakeholder.name} - {self.company.name}'

    class Meta:
        verbose_name = _('Equity')
        verbose_name_plural = _('Holdings')
        unique_together = ('stakeholder', 'company')
