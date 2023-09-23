import json
import pytest
from django.urls import reverse

def test_get(client, user1):
    response = client.get(
        reverse('user_view', kwargs={'username': 'kiryu'})
    )
    results = json.loads(response.content.decode('utf-8'))

    assert response.status_code == 200
    prof = user1.profile.serialize()
    assert prof == results

def test_get_user2(client, user2):
    response = client.get(
        reverse('user_view', kwargs={'username': 'ichiban'})
    )
    results = json.loads(response.content.decode('utf-8'))

    assert response.status_code == 200
    prof = user2.profile.serialize()
    assert prof == results

@pytest.mark.django_db
def test_get_does_not_exist(client):
    response = client.get(
        reverse('user_view', kwargs={'username': 'majima'})
    )
    results = json.loads(response.content.decode('utf-8'))

    assert response.status_code == 404
    # will have default error content
