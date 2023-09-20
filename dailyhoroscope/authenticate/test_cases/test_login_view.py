import json
import pytest
from django.conf import settings
from django.urls import reverse

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
    assert response.status_code == 200
    assert results['message'] == 'Login successful.'
    assert len(response.client.cookies[settings.SIMPLE_JWT['AUTH_COOKIE']].value) > 0
    # idk how to test for tokens... take it for granted i guess
    assert 'refresh' in results['data']
    assert 'access' in results['data']

def test_post_empty(client):
    data = {}
    response = client.post(
        reverse('login_view'),
        data=data
    )
    results = json.loads(response.content.decode('utf-8'))
    assert response.status_code == 404
    assert results['message'] == 'Invalid email or password.'
    assert settings.SIMPLE_JWT['AUTH_COOKIE'] not in response.client.cookies

def test_post_invalid_email(client, user1):
    data = {
        'username': 'wrongemail@rgg.com',
        'password': 'Password123!'
    }
    response = client.post(
        reverse('login_view'),
        data=data
    )
    results = json.loads(response.content.decode('utf-8'))
    assert response.status_code == 404
    assert settings.SIMPLE_JWT['AUTH_COOKIE'] not in response.client.cookies
    assert 'Invalid email or password.'

def test_post_invalid_password(client, user1):
    data = {
        'username': 'kazumakiryu@rgg.com',
        'password': 'wrongpassword'
    }
    response = client.post(
        reverse('login_view'),
        data=data
    )
    results = json.loads(response.content.decode('utf-8'))
    assert response.status_code == 404
    assert settings.SIMPLE_JWT['AUTH_COOKIE'] not in response.client.cookies
    assert 'Invalid email or password.'