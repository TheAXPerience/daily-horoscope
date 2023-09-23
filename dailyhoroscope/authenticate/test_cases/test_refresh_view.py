import json
import pytest
from django.conf import settings
from django.urls import reverse
from time import sleep

# if this fails because of a timeout error, it's bc the last_password_change time... is the same time
# hopefully 1 second of sleep fixes that
def test_post(client, user1):
    sleep(1)
    data = {
        'username': 'kazumakiryu@rgg.com',
        'password': 'Password123!'
    }
    response = client.post(
        reverse('login_view'),
        data=data
    )
    old_token = response.client.cookies[settings.SIMPLE_JWT['AUTH_COOKIE']].value

    response = client.post(reverse('refresh_view'))
    results = json.loads(response.content.decode('utf-8'))
    assert results['message'] == 'Tokens refreshed.'
    assert response.status_code == 200
    assert 'refresh' in results['data']
    assert 'access' in results['data']
    assert len(response.client.cookies[settings.SIMPLE_JWT['AUTH_COOKIE']].value) > 0
    assert response.client.cookies[settings.SIMPLE_JWT['AUTH_COOKIE']].value != old_token

def test_post_invalid_token(client, user1):
    response = client.post(reverse('refresh_view'))
    results = json.loads(response.content.decode('utf-8'))
    assert response.status_code == 401
    assert results['message'] == 'Invalid token submitted.'
