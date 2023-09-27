import json
import pytest
from django.urls import reverse
from horoscope.models import ReportHoroscope

def test_post(client, horoscope1):
    data = {
        'reason': "I do not have arms."
    }

    response = client.post(
        reverse('report_horoscope_view', kwargs={'hid': horoscope1.id}),
        data=data
    )
    results = json.loads(response.content.decode('utf-8'))

    assert response.status_code == 202
    assert results['message'] == 'Report has been submitted. Thank you for your time and consideration.'

    report = ReportHoroscope.objects.first()
    assert report.reported_horoscope.id == horoscope1.id
    assert report.reason == data['reason']

def test_post_html_escape(client, horoscope1):
    data = {
        'reason': "<html>I don't have arms.</html>"
    }

    response = client.post(
        reverse('report_horoscope_view', kwargs={'hid': horoscope1.id}),
        data=data
    )
    results = json.loads(response.content.decode('utf-8'))

    assert response.status_code == 202
    assert results['message'] == 'Report has been submitted. Thank you for your time and consideration.'

    report = ReportHoroscope.objects.first()
    assert report.reported_horoscope.id == horoscope1.id
    assert report.reason == "&lt;html&gt;I don&#x27;t have arms.&lt;/html&gt;"

def test_post_missing_reason(client, horoscope1):
    data = {}

    response = client.post(
        reverse('report_horoscope_view', kwargs={'hid': horoscope1.id}),
        data=data
    )
    results = json.loads(response.content.decode('utf-8'))

    assert response.status_code == 400
    assert results['message'] == 'The "reason" field must be filled out to submit a valid report.'