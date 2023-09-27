import json
import pytest
from django.urls import reverse
from django.utils import timezone

def test_get(client, dailyhoroscope):
    response = client.get(reverse('daily_horoscope_view'))
    results = json.loads(response.content.decode('utf-8'))

    assert response.status_code == 200
    assert results == dailyhoroscope.serialize()

def test_get_specific_date(client, dailyhoroscope, dailyhoroscope2):
    date = dailyhoroscope2.date
    assert date.month == 10 and date.year == 2021 and date.day == 20

    response = client.get(reverse('daily_horoscope_view') + f'?date={date.isoformat()}')
    results = json.loads(response.content.decode('utf-8'))

    assert response.status_code == 200
    assert results == dailyhoroscope2.serialize()

def test_get_incorrect_date_format(client, dailyhoroscope):
    date = '10/20/2021'

    response = client.get(reverse('daily_horoscope_view') + f'?date={date}')
    results = json.loads(response.content.decode('utf-8'))
    
    assert response.status_code == 400
    assert results['message'] == 'URL must contain a valid Date in format "YYYY-MM-DD".'

def test_get_date_not_exists(client, dailyhoroscope):
    date = '2023-10-31'

    response = client.get(reverse('daily_horoscope_view') + f'?date={date}')
    assert response.status_code == 404