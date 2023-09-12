from django.db import models
from authenticate.models import CustomUser, get_sentinel_user

# TODO: set up default horoscope for "deleted"
def get_default_horoscope():
    return Horoscope.objects.get_or_create(
        poster=get_sentinel_user(),
        horoscope="<deleted>",
    )[0]

# Create your models here.
class Horoscope(models.Model):
    poster = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="horoscopes_written"
    )
    horoscope = models.TextField(default="")
    date_posted = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def serialize(self):
        return {
            "username": self.poster.username,
            "horoscope": self.horoscope,
            "time_posted": self.date_posted,
            "last_updated": self.date_updated
        }

class DailyHoroscope(models.Model):
    date = models.DateField(auto_now_add=True)
    aries = models.ForeignKey(Horoscope, on_delete=get_default_horoscope)
    taurus = models.ForeignKey(Horoscope, on_delete=get_default_horoscope)
    gemini = models.ForeignKey(Horoscope, on_delete=get_default_horoscope)
    cancer = models.ForeignKey(Horoscope, on_delete=get_default_horoscope)
    leo = models.ForeignKey(Horoscope, on_delete=get_default_horoscope)
    virgo = models.ForeignKey(Horoscope, on_delete=get_default_horoscope)
    libra = models.ForeignKey(Horoscope, on_delete=get_default_horoscope)
    scorpio = models.ForeignKey(Horoscope, on_delete=get_default_horoscope)
    sagittarius = models.ForeignKey(Horoscope, on_delete=get_default_horoscope)
    capricorn = models.ForeignKey(Horoscope, on_delete=get_default_horoscope)
    aquarius = models.ForeignKey(Horoscope, on_delete=get_default_horoscope)
    pisces = models.ForeignKey(Horoscope, on_delete=get_default_horoscope)

    def serialize(self):
        return {
            "date": self.date,
            "aries": self.aries.serialize(),
            "taurus": self.taurus.serialize(),
            "gemini": self.gemini.serialize(),
            "cancer": self.cancer.serialize(),
            "leo": self.leo.serialize(),
            "virgo": self.virgo.serialize(),
            "libra": self.libra.serialize(),
            "scorpio": self.scorpio.serialize(),
            "sagittarius": self.sagittarius.serialize(),
            "capricorn": self.capricorn.serialize(),
            "aquarius": self.aquarius.serialize(),
            "pisces": self.pisces.serialize(),
        }

class ReportHoroscope(models.Model):
    date_reported = models.DateTimeField(auto_now_add=True)
    reported_horoscope = models.ForeignKey(Horoscope, on_delete=models.CASCADE)
    reason = models.TextField(default="")
    reviewed = models.BooleanField(default=False)

    def serialize(self):
        return {
            "date_reported": self.date_reported,
            "horoscope": self.reported_horoscope.serialize(),
            "reason": self.reason,
            "reviewed": self.reviewed,
        }
