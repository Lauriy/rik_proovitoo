import pytest
from django.conf import settings
from django.urls import reverse

from rik_proovitöö.models import LegalEntity, Equity


@pytest.fixture
def populate_db():
    owners = [LegalEntity.objects.create(name=f'Owner {i}', code=int(f'1234567890{i}'), is_person=True) for i in
              range(5)]
    companies = [LegalEntity.objects.create(name=f'Company {i}', code=int(f'654321{i}')) for i in range(12)]
    for company in companies:
        Equity.objects.create(stakeholder=owners[company.pk % len(owners)], company=company,
                              value=settings.LLC_MIN_CAPITAL)


@pytest.mark.django_db
def test_query_validation(client, populate_db):
    response = client.get(reverse('homepage'), {'query': 'ab'})

    assert 'Väärtuses peab olema vähemalt 3 tähemärki (praegu on 2).' in response.context['form'].errors['query']

    response = client.get(reverse('homepage'), {'query': ''})

    assert 'See lahter on nõutav.' in response.context['form'].errors['query']


@pytest.mark.django_db
def test_find_companies_by_name(client, populate_db):
    response = client.get(reverse('homepage'), {'query': 'Company 1'})

    assert len(response.context['company_results']) > 0


@pytest.mark.django_db
def test_find_companies_by_code(client, populate_db):
    response = client.get(reverse('homepage'), {'query': '65432'})

    assert len(response.context['company_results']) == 3


@pytest.mark.django_db
def test_find_companies_by_owner_name(client, populate_db):
    response = client.get(reverse('homepage'), {'query': 'Owner 1'})

    assert len(response.context['company_results']) > 0


@pytest.mark.django_db
def test_find_companies_by_owner_code(client, populate_db):
    response = client.get(reverse('homepage'), {'query': '12345'})

    assert len(response.context['company_results']) == 3


@pytest.mark.django_db
def test_results_pagination(client, populate_db):
    response = client.get(reverse('homepage'), {'query': 'Owner'})

    assert len(response.context['company_results']) == settings.SEARCH_RESULTS_INITIAL_LIMIT
    assert len(response.context['people_results']) == settings.SEARCH_RESULTS_INITIAL_LIMIT


@pytest.mark.django_db
def test_load_more_functionality(client, populate_db):
    response = client.get(reverse('homepage'), {'query': 'Company', 'limit': settings.SEARCH_RESULTS_MAX_LIMIT})

    assert len(response.context['company_results']) > settings.SEARCH_RESULTS_INITIAL_LIMIT


@pytest.mark.django_db
def test_pagination_limits(client, populate_db):
    response = client.get(reverse('homepage'), {'query': 'Company', 'limit': 100})

    assert len(response.context['company_results']) <= settings.SEARCH_RESULTS_MAX_LIMIT
