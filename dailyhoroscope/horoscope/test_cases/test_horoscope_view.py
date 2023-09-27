import json
import pytest
from django.shortcuts import get_object_or_404
from django.urls import reverse
from horoscope.models import Horoscope

def test_post(client, user1):
    response = client.post(
        reverse('login_view'),
        data={'username': 'papermario@ttyd.com', 'password': 'Password123!'}
    )
    results = json.loads(response.content.decode('utf-8'))
    token = results['data']['access']

    data = {
        'horoscope': 'You are never not enough for Jesus.'
    }

    response = client.post(
        reverse('horoscope_view'),
        data=data,
        headers={'AUTHORIZATION': f'Bearer {token}'}
    )
    results = json.loads(response.content.decode('utf-8'))

    assert response.status_code == 201
    assert results['message'] == 'Horoscope has been successfully uploaded.'
    assert results['data']['id']

    horoscope = get_object_or_404(Horoscope, id=results['data']['id'])
    assert horoscope is not None
    assert horoscope.id == results['data']['id']
    assert results['data']['horoscope'] == horoscope.horoscope and horoscope.horoscope == data['horoscope']

def test_post_empty(client, user1):
    response = client.post(
        reverse('login_view'),
        data={'username': 'papermario@ttyd.com', 'password': 'Password123!'}
    )
    results = json.loads(response.content.decode('utf-8'))
    token = results['data']['access']

    data = {}

    response = client.post(
        reverse('horoscope_view'),
        data=data,
        headers={'AUTHORIZATION': f'Bearer {token}'}
    )
    results = json.loads(response.content.decode('utf-8'))

    assert response.status_code == 400
    assert results['message'] == 'Request did not contain a "horoscope" field.'

def test_post_html_escape(client, user1):
    response = client.post(
        reverse('login_view'),
        data={'username': 'papermario@ttyd.com', 'password': 'Password123!'}
    )
    results = json.loads(response.content.decode('utf-8'))
    token = results['data']['access']

    data = {
        'horoscope': '<p>You are never not enough for Jesus.</p>'
    }

    response = client.post(
        reverse('horoscope_view'),
        data=data,
        headers={'AUTHORIZATION': f'Bearer {token}'}
    )
    results = json.loads(response.content.decode('utf-8'))

    assert response.status_code == 201
    assert results['message'] == 'Horoscope has been successfully uploaded.'
    assert results['data']['id']

    horoscope = get_object_or_404(Horoscope, id=results['data']['id'])
    assert horoscope is not None
    assert results['data']['horoscope'] == horoscope.horoscope and horoscope.horoscope == '&lt;p&gt;You are never not enough for Jesus.&lt;/p&gt;'
