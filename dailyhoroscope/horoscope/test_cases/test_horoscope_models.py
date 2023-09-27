from horoscope.models import DATE_FORMAT, DATETIME_FORMAT

def test_horoscope_serialize(horoscope1):
    result = horoscope1.serialize()
    assert result['id'] == horoscope1.id
    assert result['username'] == horoscope1.poster.username
    assert result['horoscope'] == horoscope1.horoscope
    assert result['time_posted'] == horoscope1.date_posted.strftime(DATETIME_FORMAT)
    assert result['last_updated'] == horoscope1.date_updated.strftime(DATETIME_FORMAT)


def test_daily_horoscope_serialize(dailyhoroscope):
    result = dailyhoroscope.serialize()
    assert result['date'] == dailyhoroscope.date.strftime(DATE_FORMAT)
    assert result['aries'] == dailyhoroscope.aries.serialize()
    assert result['taurus'] == dailyhoroscope.taurus.serialize()
    assert result['gemini'] == dailyhoroscope.gemini.serialize()
    assert result['cancer'] == dailyhoroscope.cancer.serialize()
    assert result['leo'] == dailyhoroscope.leo.serialize()
    assert result['virgo'] == dailyhoroscope.virgo.serialize()
    assert result['libra'] == dailyhoroscope.libra.serialize()
    assert result['scorpio'] == dailyhoroscope.scorpio.serialize()
    assert result['sagittarius'] == dailyhoroscope.sagittarius.serialize()
    assert result['capricorn'] == dailyhoroscope.capricorn.serialize()
    assert result['aquarius'] == dailyhoroscope.aquarius.serialize()
    assert result['pisces'] == dailyhoroscope.pisces.serialize()

def test_report_horoscope_serialize(reporthoroscope):
    result = reporthoroscope.serialize()
    assert result['date_reported'] == reporthoroscope.date_reported.strftime(DATETIME_FORMAT)
    assert result['horoscope'] == reporthoroscope.reported_horoscope.serialize()
    assert result['reason'] == reporthoroscope.reason
    assert result['reviewed'] == reporthoroscope.reviewed