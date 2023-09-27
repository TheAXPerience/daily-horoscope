import json
import pytest
from django.urls import reverse

def test_get(client, user1, horoscope1, horoscope2, horoscope3):
    response = client.get(
        reverse('user_horoscope_view', kwargs={'username': user1.username})
    )
    results = json.loads(response.content.decode('utf-8'))

    assert response.status_code == 200
    assert len(results) == 2
    assert results[0] == horoscope2.serialize()
    assert results[1] == horoscope1.serialize()

@pytest.mark.django_db
def test_get_user_not_exists(client):
    response = client.get(
        reverse('user_horoscope_view', kwargs={'username': 'BobMarley'})
    )

    assert response.status_code == 404