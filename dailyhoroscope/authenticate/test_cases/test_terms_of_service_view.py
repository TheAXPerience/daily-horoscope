import json
import pytest
from django.urls import reverse
from authenticate.termsofservice import TERMS_OF_SERVICE

def test_get(client):
    response = client.get(reverse('terms_of_service_view'))
    results = json.loads(response.content.decode('utf-8'))

    assert response.status_code == 200
    assert results == TERMS_OF_SERVICE
