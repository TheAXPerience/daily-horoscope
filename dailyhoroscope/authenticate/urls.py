from django.urls import path
from authenticate import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('register', views.RegisterView.as_view(), name='register_view'),
    path('login', views.LoginView.as_view(), name='login_view'),
    path('user', views.UserView.as_view(), name='user_view'),
    path('change-password', views.ChangePasswordView.as_view(), name='change_password_view'),
    path('refresh', views.RefreshView.as_view(), name='refresh_view')
]