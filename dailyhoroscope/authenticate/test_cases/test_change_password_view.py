import json
import pytest
from django.shortcuts import get_object_or_404
from django.urls import reverse
from authenticate.models import CustomUser

def test_put(client, user2):
    response = client.post(
        reverse('login_view'),
        data={'username': 'kasugaichiban@ichiban.holdings', 'password': 'Password123!'}
    )
    results = json.loads(response.content.decode('utf-8'))
    token = results['data']['access']

    response = client.put(
        reverse('change_password_view'), 
        data = {
            'old_password': 'Password123!', 
            'new_password': 'IchibanHolding$1'
        },
        headers={'AUTHORIZATION': f'Bearer {token}'},
        content_type='application/json'
    )
    results = json.loads(response.content.decode('utf-8'))
    assert response.status_code == 202
    assert results['message'] == 'Password changed successfully.'

    user = CustomUser.objects.filter(username='ichiban').first()
    assert not user.check_password('Password123!')
    assert user.check_password('IchibanHolding$1')
    assert user.last_password_change > user2.last_password_change

def test_put_unauthenticated(client):
    response = client.put(
        reverse('change_password_view'), 
        data = {
            'old_password': 'Password123!', 
            'new_password': 'IchibanHolding$1'
        },
        content_type='application/json'
    )
    results = json.loads(response.content.decode('utf-8'))
    assert response.status_code == 401
    assert results['detail'] == 'Authentication credentials were not provided.'

def test_put_empty(client, user2):
    response = client.post(
        reverse('login_view'),
        data={'username': 'kasugaichiban@ichiban.holdings', 'password': 'Password123!'}
    )
    results = json.loads(response.content.decode('utf-8'))
    token = results['data']['access']

    response = client.put(
        reverse('change_password_view'), 
        data = {},
        headers={'AUTHORIZATION': f'Bearer {token}'},
        content_type='application/json'
    )
    results = json.loads(response.content.decode('utf-8'))
    assert response.status_code == 400
    assert results['message'] == 'Incorrect/missing data submitted.'

def test_put_incorrect_password(client, user2):
    response = client.post(
        reverse('login_view'),
        data={'username': 'kasugaichiban@ichiban.holdings', 'password': 'Password123!'}
    )
    results = json.loads(response.content.decode('utf-8'))
    token = results['data']['access']

    response = client.put(
        reverse('change_password_view'), 
        data = {
            'old_password': 'wrongPassword!', 
            'new_password': 'IchibanHolding$1'
        },
        headers={'AUTHORIZATION': f'Bearer {token}'},
        content_type='application/json'
    )
    results = json.loads(response.content.decode('utf-8'))
    assert response.status_code == 400
    assert results['message'] == 'Entered incorrect password. Password change denied.'

def test_put_password_not_allowed(client, user2):
    response = client.post(
        reverse('login_view'),
        data={'username': 'kasugaichiban@ichiban.holdings', 'password': 'Password123!'}
    )
    results = json.loads(response.content.decode('utf-8'))
    token = results['data']['access']

    response = client.put(
        reverse('change_password_view'), 
        data = {
            'old_password': 'Password123!', 
            'new_password': 'ichibanholdings'
        },
        headers={'AUTHORIZATION': f'Bearer {token}'},
        content_type='application/json'
    )
    results = json.loads(response.content.decode('utf-8'))
    assert response.status_code == 400
    assert results['message'] == 'password must contain at least one lowercase letter, one uppercase letter, one digit, and one special character.'
