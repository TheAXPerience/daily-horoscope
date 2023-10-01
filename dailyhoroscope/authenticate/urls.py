from django.urls import path
from authenticate import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('register', views.RegisterView.as_view(), name='register_view'),
    path('login', views.LoginView.as_view(), name='login_view'),
    path('user/<str:username>', views.UserView.as_view(), name='user_view'),
    path('change-password', views.ChangePasswordView.as_view(), name='change_password_view'),
    path('reset-password', views.ResetPasswordRequestView.as_view(), name='reset_password-request-view'),
    path('reset-password/reset', views.ResetPasswordView.as_view(), name='reset_password-view'),
    path('refresh', views.RefreshView.as_view(), name='refresh_view'),
    path('logout', views.LogoutView.as_view(), name='logout_view'),
    path('profile', views.ProfileChangesView.as_view(), name='profile_view'),
    path('termsofservice', views.TermsOfServiceView.as_view(), name='terms_of_service_view'),
]
