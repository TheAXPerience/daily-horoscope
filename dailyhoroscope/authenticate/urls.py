from django.urls import path
from authenticate import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('register', views.RegisterView.as_view(), name='register_view'),
]