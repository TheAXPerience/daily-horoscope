from django.urls import path 
from horoscope import views 
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('', views.HoroscopeView.as_view(), name='horoscope_view'),
    path('<int:hid>', views.SingularHoroscopeView.as_view(), name='singular_horoscope_view'),
    path('report/<int:hid>', views.ReportHoroscopeView.as_view(), name='report_horoscope_view'),
    path('user/<str:username>', views.UserHoroscopeView.as_view(), name='user_horoscope_view'),
    path('daily', views.DailyHoroscopeView.as_view(), name='daily_horoscope_view'),
]