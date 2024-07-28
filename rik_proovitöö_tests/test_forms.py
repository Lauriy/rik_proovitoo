import pytest
from django.test import Client
from django.urls import reverse

from rik_proovitöö.models import LegalEntity


@pytest.fixture
def client():
    return Client()


@pytest.mark.django_db
def test_create_and_edit_llc(client):
    stakeholder1 = LegalEntity.objects.create(
        name='Stakeholder 1',
        code='39004020251',
        is_person=True
    )
    stakeholder2 = LegalEntity.objects.create(
        name='Stakeholder 2',
        code='37107262211',
        is_person=True
    )

    create_url = reverse('establish_llc')
    create_data = {
        'name': 'Test LLC',
        'code': '1234567',
        'creation_date': '2023-01-01',
        'capital': 2500,
        'stakes-TOTAL_FORMS': '1',
        'stakes-INITIAL_FORMS': '0',
        'stakes-MIN_NUM_FORMS': '0',
        'stakes-MAX_NUM_FORMS': '1000',
        'stakes-0-stakeholder': stakeholder1.id,
        'stakes-0-value': 2500,
    }
    response = client.post(create_url, create_data)
    assert response.status_code == 302

    legal_entity = LegalEntity.objects.get(code='1234567')
    assert legal_entity.name == 'Test LLC'
    assert legal_entity.capital == 2500
    assert legal_entity.stakes.count() == 1

    edit_url = reverse('edit_llc', args=[legal_entity.code])
    edit_data = {
        'name': 'Test LLC Updated',
        'code': '1234567',
        'creation_date': '2023-01-01',
        'capital': 2500,
        'stakes-TOTAL_FORMS': '2',
        'stakes-INITIAL_FORMS': '1',
        'stakes-MIN_NUM_FORMS': '0',
        'stakes-MAX_NUM_FORMS': '1000',
        'stakes-0-id': legal_entity.stakes.first().id,
        'stakes-0-company': legal_entity.id,
        'stakes-0-stakeholder': stakeholder1.id,
        'stakes-0-value': 1250,
        'stakes-1-company': legal_entity.id,
        'stakes-1-stakeholder': stakeholder2.id,
        'stakes-1-value': 1250,
    }
    response = client.post(edit_url, edit_data)
    assert response.status_code == 302

    legal_entity.refresh_from_db()
    assert legal_entity.name == 'Test LLC Updated'
    assert legal_entity.stakes.count() == 2

    old_equity = legal_entity.stakes.get(stakeholder=stakeholder1)
    assert old_equity.is_founding

    new_equity = legal_entity.stakes.get(stakeholder=stakeholder2)
    assert not new_equity.is_founding
