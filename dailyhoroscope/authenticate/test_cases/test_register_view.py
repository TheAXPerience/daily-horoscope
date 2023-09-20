import datetime
from django.utils import timezone
import json
import pytest
from authenticate.models import CustomUser, UserProfile
from django.shortcuts import get_object_or_404
from django.urls import reverse

@pytest.mark.django_db
def test_post(client):
    dob = timezone.now()
    dob_day = dob.day - 1
    dob_month = dob.month
    dob_year = dob.year-13
    if dob_day == 0:
        dob_day = 28
        dob_month -= 1
        if dob_month == 0:
            dob_month = 12
            dob_year -= 1
    dob = dob.replace(year=dob_year, day=dob_day, month=dob_month)
    data = {
        'email': 'hello@world.com',
        'username': 'hello',
        'password': 'Password123!',
        'date_of_birth': dob.date().isoformat(),
        'accept_tos': "TRUE"
    }
    response = client.post(
        reverse('register_view'),
        data=data
    )
    results = json.loads(response.content.decode('utf-8'))
    assert results['message'] == 'New user registered.'
    assert response.status_code == 200
    
    assert results['data']['username'] == data['username']
    
    newuser = get_object_or_404(CustomUser, username=data['username'])
    assert newuser.check_password(data['password'])
    assert newuser.accept_tos
    assert newuser.date_of_birth == datetime.datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
    assert newuser.username == data['username']
    assert newuser.email == data['email']

@pytest.mark.django_db
def test_post_empty(client):
    data = {
    }
    response = client.post(
        reverse('register_view'),
        data=data
    )
    results = json.loads(response.content.decode('utf-8'))
    assert len(results['message']) == 5
    assert results['message'][0] == 'email field must not be empty.'
    assert results['message'][1] == 'username field must not be empty.'
    assert results['message'][2] == 'password field must not be empty.'
    assert results['message'][3] == 'date_of_birth field must not be empty.'
    assert results['message'][4] == 'accept_tos field must not be empty.'
    assert response.status_code == 400

@pytest.mark.django_db
def test_post_email_not_allowed(client):
    data = {
        'email': 'hello_world',
        'username': 'hello',
        'password': 'Password123!',
        'date_of_birth': '2004-05-05',
        'accept_tos': "TRUE"
    }
    response = client.post(
        reverse('register_view'),
        data=data
    )
    results = json.loads(response.content.decode('utf-8'))
    assert results['message'][0] == 'email field must be a valid email address.'
    assert response.status_code == 400

@pytest.mark.django_db
def test_post_email_taken(client, user1):
    data = {
        'email': 'kazumakiryu@rgg.com',
        'username': 'hello',
        'password': 'Password123!',
        'date_of_birth': '2004-05-05',
        'accept_tos': "TRUE"
    }
    response = client.post(
        reverse('register_view'),
        data=data
    )
    results = json.loads(response.content.decode('utf-8'))
    assert results['message'][0] == 'A user with the given email already exists.'
    assert response.status_code == 400

@pytest.mark.django_db
def test_post_username_not_allowed(client):
    data = {
        'email': 'hello@world.com',
        'username': 'hello world',
        'password': 'Password123!',
        'date_of_birth': '2004-05-05',
        'accept_tos': "TRUE"
    }
    response = client.post(
        reverse('register_view'),
        data=data
    )
    results = json.loads(response.content.decode('utf-8'))
    assert results['message'][0] == 'username must consist of only letters, numbers, and underscores.'
    assert response.status_code == 400

@pytest.mark.django_db
def test_post_username_taken(client, user1):
    data = {
        'email': 'hello@world.com',
        'username': 'kiryu',
        'password': 'Password123!',
        'date_of_birth': '2004-05-05',
        'accept_tos': "TRUE"
    }
    response = client.post(
        reverse('register_view'),
        data=data
    )
    results = json.loads(response.content.decode('utf-8'))
    assert results['message'][0] == 'A user with the given username already exists.'
    assert response.status_code == 400

@pytest.mark.django_db
def test_post_password_not_allowed(client):
    data = {
        'email': 'hello@world.com',
        'username': 'hello',
        'password': 'password',
        'date_of_birth': '2004-05-05',
        'accept_tos': "TRUE"
    }
    response = client.post(
        reverse('register_view'),
        data=data
    )
    results = json.loads(response.content.decode('utf-8'))
    assert results['message'][0] == 'password must contain at least one lowercase letter, one uppercase letter, one digit, and one special character.'
    assert response.status_code == 400

@pytest.mark.django_db
def test_post_age_too_young(client):
    dob = timezone.now()
    dob = dob.replace(year=dob.year - 12)
    data = {
        'email': 'hello@world.com',
        'username': 'hello',
        'password': 'Password123!',
        'date_of_birth': dob.date().isoformat(),
        'accept_tos': "TRUE"
    }
    response = client.post(
        reverse('register_view'),
        data=data
    )
    results = json.loads(response.content.decode('utf-8'))
    assert results['message'][0] == 'Age must be greater than or equal to 13.'
    assert response.status_code == 400
