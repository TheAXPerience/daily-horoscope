import json
import pytest
from django.shortcuts import get_object_or_404
from django.urls import reverse
from authenticate.models import CustomUser

def test_get(client, profile2):
    prof, _ = profile2

    response = client.post(
        reverse('login_view'),
        data={'username': 'kasugaichiban@ichiban.holdings', 'password': 'Password123!'}
    )
    results = json.loads(response.content.decode('utf-8'))
    token = results['data']['access']

    response = client.get(reverse('profile_view'), headers={'AUTHORIZATION': f'Bearer {token}'})
    results = json.loads(response.content.decode('utf-8'))

    assert response.status_code == 200
    assert results['description'] == prof.description
    assert results['dob_public'] == prof.dob_public
    assert results['email_public'] == prof.email_public
    assert results['subscribed_to_newsletter'] == prof.subscribed_to_newsletter

@pytest.mark.django_db
def test_put(client, profile2):
    prof, _ = profile2

    response = client.post(
        reverse('login_view'),
        data={'username': 'kasugaichiban@ichiban.holdings', 'password': 'Password123!'}
    )
    results = json.loads(response.content.decode('utf-8'))
    token = results['data']['access']

    response = client.put(
        reverse('profile_view'), 
        data = {
            'description': 'Owner of Ichiban Holdings', 
            'dob_public': True,
            'email_public': True,
            'subscribed_to_newsletter': True
        },
        headers={'AUTHORIZATION': f'Bearer {token}'},
        content_type='application/json'
    )
    results = json.loads(response.content.decode('utf-8'))
    assert response.status_code == 202
    assert results['message'] == 'User\'s profile settings have been updated.'

    user = get_object_or_404(CustomUser, username='ichiban')
    assert user.profile.description == 'Owner of Ichiban Holdings'
    assert user.profile.dob_public
    assert user.profile.email_public
    assert user.profile.subscribed_to_newsletter

def test_put_html_escape(client, profile2):
    prof, _ = profile2

    response = client.post(
        reverse('login_view'),
        data={'username': 'kasugaichiban@ichiban.holdings', 'password': 'Password123!'}
    )
    results = json.loads(response.content.decode('utf-8'))
    token = results['data']['access']

    response = client.put(
        reverse('profile_view'), 
        data = {
            'description': '<html>Owner of Ichiban Holdings</html>', 
            'dob_public': True,
            'email_public': True,
            'subscribed_to_newsletter': True
        },
        headers={'AUTHORIZATION': f'Bearer {token}'},
        content_type='application/json'
    )
    results = json.loads(response.content.decode('utf-8'))
    assert response.status_code == 202
    assert results['message'] == 'User\'s profile settings have been updated.'

    user = get_object_or_404(CustomUser, username='ichiban')
    assert user.profile.description == '&lt;html&gt;Owner of Ichiban Holdings&lt;/html&gt;'
    assert user.profile.dob_public
    assert user.profile.email_public
    assert user.profile.subscribed_to_newsletter

def test_put_unauthenticated(client):
    response = client.put(
        reverse('profile_view'), 
        data = {
            'description': '<html>Owner of Ichiban Holdings</html>', 
            'dob_public': True,
            'email_public': True,
            'subscribed_to_newsletter': True
        },
        content_type='application/json'
    )
    results = json.loads(response.content.decode('utf-8'))
    assert response.status_code == 401
    assert results['detail'] == 'Authentication credentials were not provided.'

def test_delete(client, profile2):
    response = client.post(
        reverse('login_view'),
        data={'username': 'kasugaichiban@ichiban.holdings', 'password': 'Password123!'}
    )
    results = json.loads(response.content.decode('utf-8'))
    token = results['data']['access']

    response = client.delete(
        reverse('profile_view'), 
        headers={'AUTHORIZATION': f'Bearer {token}'}
    )
    results = json.loads(response.content.decode('utf-8'))
    assert response.status_code == 202
    assert results['message'] == 'User successfully deleted.'

    assert not CustomUser.objects.filter(username='ichiban').exists()

def test_delete_unauthenticated(client):
    response = client.delete(
        reverse('profile_view')
    )
    results = json.loads(response.content.decode('utf-8'))
    assert response.status_code == 401
    assert results['detail'] == 'Authentication credentials were not provided.'
