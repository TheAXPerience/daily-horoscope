import datetime
import pytest
from horoscope.models import Horoscope, DailyHoroscope

@pytest.fixture
def user1(db, django_user_model):
    birthdate = '1999-09-11'
    user = django_user_model.objects.create_user(
        email='papermario@ttyd.com',
        username='GoombellaGirl',
        password='Password123!',
        date_of_birth=datetime.datetime.strptime(birthdate, '%Y-%m-%d').date(),
        accept_tos=True
    )
    yield user

@pytest.fixture
def user2(db, django_user_model):
    birthdate = '1999-04-13'
    user = django_user_model.objects.create_user(
        email='marioluigi@superstar.com',
        username='PrincessDaisy',
        password='Password123!',
        date_of_birth=datetime.datetime.strptime(birthdate, '%Y-%m-%d').date(),
        accept_tos=True
    )
    yield user

@pytest.fixture
def horoscope1(user1):
    horoscope = Horoscope.objects.create(
        poster=user1,
        horoscope='Life can get hard, but at least you have arms.'
    )
    yield horoscope

@pytest.fixture
def horoscope2(user1):
    horoscope = Horoscope.objects.create(
        poster=user1,
        horoscope='Reading is a skill that helps grow your mind. And your skull strength.'
    )
    yield horoscope

@pytest.fixture
def horoscope3(user2):
    horoscope = Horoscope.objects.create(
        poster=user2,
        horoscope='When things get tough, you can always rely on the brothers. Lets-a go, a-Mario Bros.'
    )
    yield horoscope

@pytest.fixture
def dailyhoroscope(horoscope1, horoscope2, horoscope3):
    horoscopes = DailyHoroscope.objects.create(
        aries=horoscope1,
        taurus=horoscope2,
        gemini=horoscope1,
        cancer=horoscope1,
        leo=horoscope3,
        virgo=horoscope2,
        libra=horoscope1,
        scorpio=horoscope3,
        sagittarius=horoscope2,
        capricorn=horoscope3,
        aquarius=horoscope3,
        pisces=horoscope2
    )
    yield horoscopes
