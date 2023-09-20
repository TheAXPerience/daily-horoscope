from authenticate.models import CustomUser, UserProfile
import datetime
import pytest

@pytest.mark.django_db
@pytest.fixture
def user1(db, django_user_model):
    birthdate = '2000-01-01'
    user = django_user_model.objects.create_user(
        email='kazumakiryu@rgg.com',
        username='kiryu',
        password='Password123!',
        date_of_birth=datetime.datetime.strptime(birthdate, '%Y-%m-%d').date(),
        accept_tos=True
    )
    yield user

@pytest.mark.django_db
@pytest.fixture
def profile1(db, user1):
    profile = user1.profile
    profile.description = 'The Dragon of Dojima'
    profile.dob_public = True
    profile.email_public = True
    profile.subscribed_to_newsletter = True
    profile.save()
    yield profile, user1

@pytest.mark.django_db
@pytest.fixture
def user2(db, django_user_model):
    birthdate = '2001-02-02'
    user = django_user_model.objects.create_user(
        email='kasugaichiban@ichiban.holdings',
        username='ichiban',
        password='Password123!',
        date_of_birth=datetime.datetime.strptime(birthdate, '%Y-%m-%d').date(),
        accept_tos=True
    )
    yield user

@pytest.mark.django_db
@pytest.fixture
def profile2(db, user2):
    profile = user2.profile
    profile.description = 'Coin Locker Baby'
    profile.dob_public = False
    profile.email_public = False
    profile.subscribed_to_newsletter = False
    profile.save()
    yield profile, user2
