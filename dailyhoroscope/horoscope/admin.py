from django.contrib import admin
from .models import Horoscope, DailyHoroscope, ReportHoroscope

# Register your models here.
@admin.register(Horoscope)
class HoroscopeAdmin(admin.ModelAdmin):
    list_display = [
        "id", "poster", "horoscope", "date_posted", "date_updated"
    ]

@admin.register(DailyHoroscope)
class DailyHoroscopeAdmin(admin.ModelAdmin):
    list_display = [
        "id", "date"
    ]

@admin.register(ReportHoroscope)
class HoroscopeAdmin(admin.ModelAdmin):
    list_display = [
        "id", "reported_horoscope", "date_reported", "reviewed"
    ]
