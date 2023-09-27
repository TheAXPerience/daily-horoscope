import json
import pytest
from django.shortcuts import get_object_or_404
from django.urls import reverse
from horoscope.models import Horoscope

def test_get(client, horoscope1):
    response = client.get(
        reverse('singular_horoscope_view', kwargs={'hid': horoscope1.id})
    )
    results = json.loads(response.content.decode('utf-8'))

    assert response.status_code == 200
    assert results == horoscope1.serialize()

def test_put(client, horoscope1):
    response = client.post(
        reverse('login_view'),
        data={'username': 'papermario@ttyd.com', 'password': 'Password123!'}
    )
    results = json.loads(response.content.decode('utf-8'))
    token = results['data']['access']

    data = {'horoscope': 'Life can get hard, but at least you are not a goomba.'}

    response = client.put(
        reverse('singular_horoscope_view', kwargs={'hid': horoscope1.id}),
        data=data,
        headers={'AUTHORIZATION': f'Bearer {token}'},
        content_type='application/json'
    )
    results = json.loads(response.content.decode('utf-8'))

    assert response.status_code == 202
    assert results['message'] == f'Horoscope #{horoscope1.id} successfully changed.'
    
    horoscope = get_object_or_404(Horoscope, id=horoscope1.id)
    assert horoscope.horoscope == data['horoscope']
    assert horoscope.date_updated > horoscope1.date_updated


def test_put_html_escape(client, horoscope1):
    response = client.post(
        reverse('login_view'),
        data={'username': 'papermario@ttyd.com', 'password': 'Password123!'}
    )
    results = json.loads(response.content.decode('utf-8'))
    token = results['data']['access']

    data = {'horoscope': '<html>Life is hard.</html>'}

    response = client.put(
        reverse('singular_horoscope_view', kwargs={'hid': horoscope1.id}),
        data=data,
        headers={'AUTHORIZATION': f'Bearer {token}'},
        content_type='application/json'
    )
    results = json.loads(response.content.decode('utf-8'))

    assert response.status_code == 202
    assert results['message'] == f'Horoscope #{horoscope1.id} successfully changed.'
    
    horoscope = get_object_or_404(Horoscope, id=horoscope1.id)
    assert horoscope.horoscope == '&lt;html&gt;Life is hard.&lt;/html&gt;'
    assert horoscope.date_updated > horoscope1.date_updated

def test_put_incorrect_user(client, user1, horoscope3):
    response = client.post(
        reverse('login_view'),
        data={'username': 'papermario@ttyd.com', 'password': 'Password123!'}
    )
    results = json.loads(response.content.decode('utf-8'))
    token = results['data']['access']

    data = {'horoscope': '<html>Life is hard.</html>'}

    response = client.put(
        reverse('singular_horoscope_view', kwargs={'hid': horoscope3.id}),
        data=data,
        headers={'AUTHORIZATION': f'Bearer {token}'},
        content_type='application/json'
    )
    results = json.loads(response.content.decode('utf-8'))

    assert response.status_code == 403
    assert results['message'] == 'The current logged-in user does not have the permissions to change another user\'s horoscopes.'

def test_put_no_data(client, horoscope1):
    response = client.post(
        reverse('login_view'),
        data={'username': 'papermario@ttyd.com', 'password': 'Password123!'}
    )
    results = json.loads(response.content.decode('utf-8'))
    token = results['data']['access']

    data = {}

    response = client.put(
        reverse('singular_horoscope_view', kwargs={'hid': horoscope1.id}),
        data=data,
        headers={'AUTHORIZATION': f'Bearer {token}'},
        content_type='application/json'
    )
    results = json.loads(response.content.decode('utf-8'))

    assert response.status_code == 400
    assert results['message'] == 'A change in data was not submitted.'

def test_delete(client, horoscope1):
    response = client.post(
        reverse('login_view'),
        data={'username': 'papermario@ttyd.com', 'password': 'Password123!'}
    )
    results = json.loads(response.content.decode('utf-8'))
    token = results['data']['access']

    response = client.delete(
        reverse('singular_horoscope_view', kwargs={'hid': horoscope1.id}),
        headers={'AUTHORIZATION': f'Bearer {token}'}
    )
    results = json.loads(response.content.decode('utf-8'))

    assert response.status_code == 200
    assert results['message'] == 'Horoscope successfully deleted.'

def test_delete_incorrect_user(client, user1, horoscope3):
    response = client.post(
        reverse('login_view'),
        data={'username': 'papermario@ttyd.com', 'password': 'Password123!'}
    )
    results = json.loads(response.content.decode('utf-8'))
    token = results['data']['access']

    response = client.delete(
        reverse('singular_horoscope_view', kwargs={'hid': horoscope3.id}),
        headers={'AUTHORIZATION': f'Bearer {token}'}
    )
    results = json.loads(response.content.decode('utf-8'))

    assert response.status_code == 403
    assert results['message'] == 'The current logged-in user does not have the permissions to delete another user\'s horoscopes.'