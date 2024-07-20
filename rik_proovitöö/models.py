from datetime import date

from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MinValueValidator, MaxValueValidator
from django.db.models import CharField, Model, DateField, IntegerField, CASCADE, ForeignKey, DateTimeField, \
    BooleanField, Sum, Index
from django.utils import timezone


class CreatedUpdatedMixin:
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)


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


def no_future_date(value):
    if value > timezone.now().date():
        raise ValidationError('Legal entities cannot be established into the future')


class LegalEntity(Model, CreatedUpdatedMixin):
    name = CharField(max_length=100, validators=[
        MinLengthValidator(3),
    ])
    code = IntegerField(validators=[
        MinValueValidator(1000000),  # 7 digits is the minimum for OÜ-s
        MaxValueValidator(99999999999),  # 11 digits is the maximum for personal codes
    ])
    creation_date = DateField(validators=[no_future_date], blank=True)
    capital = IntegerField(null=True)  # People don't have this
    is_person = BooleanField(default=False)

    def __str__(self):
        return f'{self.name} ({self.code})'

    def clean(self):
        super().clean()
        if self.is_person:
            if len(str(self.code)) != 11:
                raise ValidationError('Personal codes must be 11 digits long')
            is_check_digit_correct = _calculate_personal_check_digit(self.code) == int(str(self.code)[-1])
            if not is_check_digit_correct:
                raise ValidationError('Personal code check digit is incorrect')
            self.creation_date = _convert_to_birthdate(self.code)
        else:
            if len(str(self.code)) != 7:
                raise ValidationError('Business codes must be 7 digits long')
            if not self.creation_date:
                raise ValidationError('Businesses must have an establishment date specified')
            if self.capital < settings.LLC_MIN_CAPITAL:
                raise ValidationError(f'Businesses must have at least {settings.LLC_MIN_CAPITAL} capital')
            total_equity = self.stakes.aggregate(Sum('value'))['value__sum'] or 0
            if total_equity != self.capital:
                raise ValidationError(
                    f'Total equity holdings ({total_equity}) do not match the company\'s capital ({self.capital})')

    class Meta:
        verbose_name = 'Legal entity'
        verbose_name_plural = 'Legal entities'
        indexes = [
            Index(fields=['code']),  # Regular index for URL traversal
            GinIndex(fields=['code', 'name']),  # GinIndex for search
        ]


class Equity(Model, CreatedUpdatedMixin):
    stakeholder = ForeignKey('LegalEntity', on_delete=CASCADE, related_name='holdings')
    company = ForeignKey('LegalEntity', on_delete=CASCADE, related_name='stakes')
    value = IntegerField()
    is_founding = BooleanField(default=True)

    def __str__(self):
        return f'{self.stakeholder.name} - {self.company.name}'

    class Meta:
        verbose_name = 'Equity'
        verbose_name_plural = 'Holdings'
        unique_together = ('stakeholder', 'company')
