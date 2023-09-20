import json
import pytest
from django.conf import settings
from django.urls import reverse
from http.cookies import SimpleCookie

@pytest.mark.django_db
def test_post(client, user1):
    data = {
        'username': 'kazumakiryu@rgg.com',
        'password': 'Password123!'
    }
    response = client.post(
        reverse('login_view'),
        data=data
    )
    results = json.loads(response.content.decode('utf-8'))
    token = results['data']['access']

    response = client.post(
        reverse('logout_view'),
        headers={'AUTHORIZATION': f'Bearer {token}'}
    )
    results = json.loads(response.content.decode('utf-8'))
    assert results['message'] == 'Successfully logged out.'
    assert response.client.cookies[settings.SIMPLE_JWT['AUTH_COOKIE']].value == ''
    assert response.status_code == 200

@pytest.mark.django_db
def test_post_no_token(client, user1):
    data = {
        'username': 'kazumakiryu@rgg.com',
        'password': 'Password123!'
    }
    response = client.post(
        reverse('login_view'),
        data=data
    )
    results = json.loads(response.content.decode('utf-8'))

    response = client.post(
        reverse('logout_view')
    )
    results = json.loads(response.content.decode('utf-8'))
    assert response.status_code == 401
    assert results['detail'] == 'Authentication credentials were not provided.'

@pytest.mark.django_db
def test_post_no_refresh(client, user1):
    data = {
        'username': 'kazumakiryu@rgg.com',
        'password': 'Password123!'
    }
    response = client.post(
        reverse('login_view'),
        data=data
    )
    results = json.loads(response.content.decode('utf-8'))
    token = results['data']['access']

    client.cookies = SimpleCookie({})
    response = client.post(
        reverse('logout_view'),
        headers={'AUTHORIZATION': f'Bearer {token}'}
    )
    results = json.loads(response.content.decode('utf-8'))
    assert results['message'] == 'User already logged out.'
    assert response.status_code == 401
