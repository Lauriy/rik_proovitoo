from datetime import date

import pytest

from rik_proovitöö.models import LegalEntity, Equity


@pytest.mark.django_db
def test_can_create_valid_person():
    valid_person = LegalEntity(name='Lauri Elias', code=39004020251, is_person=True)
    valid_person.full_clean()
    valid_person.save()

    assert valid_person.creation_date == date(1990, 4, 2)


@pytest.mark.django_db
@pytest.mark.parametrize("name, code, is_person, creation_date, capital, expected_error", [
    ('', 39004020251, True, None, None, 'See väli ei saa olla tühi'),  # Name too short
    ('Lauri Elias', 123, True, None, None, 'Isikukood peab olema 11-kohaline arv'),  # Personal code too short
    ('Lauri Elias', 3900402025, True, None, None, 'Isikukood peab olema 11-kohaline arv'),  # Personal code too short
    ('Lauri Elias', 390040202512, True, None, None, 'Isikukood peab olema 11-kohaline arv'),  # Personal code too long
    ('Lauri Elias', 39004020250, True, None, None, 'Isikukoodi kontrollnumber ei ole õige'),  # Invalid check digit
    ('Indoorsman OÜ', 123456, False, None, None, 'Äriregistri kood peab olema 7-kohaline arv'),
    # Business code too short
    ('Indoorsman OÜ', 12345678, False, None, None, 'Äriregistri kood peab olema 7-kohaline arv'),
    # Business code too long
    ('Indoorsman OÜ', 1234567, False, None, None, 'Osaühingutele peab määrama asutamiskuupäeva'),
    # Missing creation date
    ('Indoorsman OÜ', 1234567, False, date(2015, 10, 5), None, 'Osaühingutel peab olema vähemalt 2500 eurot kapitali'),
    # Missing capital
])
def test_cant_create_invalid_person(name, code, is_person, creation_date, capital, expected_error):
    try:
        invalid_entity = LegalEntity(name=name, code=code, is_person=is_person, creation_date=creation_date,
                                     capital=capital)
        invalid_entity.full_clean()
    except Exception as e:
        assert expected_error in str(e)
    else:
        pytest.fail("Expected error was not raised")


@pytest.mark.django_db
def test_can_create_valid_company():
    # Hardcoded IDs to avoid saving before everything validates
    valid_person = LegalEntity(name='Lauri Elias', code=39004020251, is_person=True)
    valid_person.full_clean()
    valid_person.save()
    # Real code 12925233, requirement in this project is 7 digits
    valid_company = LegalEntity(name='Indoorsman OÜ', code=1292523, creation_date=date(2015, 10, 5),
                                capital=2500)
    equity = Equity(stakeholder=valid_person, company=valid_company, value=2500)
    valid_company.save()
    equity.save()
    valid_company.full_clean()

    assert valid_company.pk
