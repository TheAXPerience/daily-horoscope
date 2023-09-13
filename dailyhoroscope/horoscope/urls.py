from django.urls import path 
from horoscope import views 
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('', views.HoroscopeView.as_view(), 'horoscope_view'),
    path('<int:hid>', views.SingularHoroscopeView.as_view(), 'singular_horoscope_view'),
    path('report/<int:hid>', views.ReportHoroscopeView.as_view(), 'report_horoscope_view'),
    path('user/<str:username>', views.UserHoroscipeView.as_view(), 'user_horoscope_view'),
]