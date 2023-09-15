from django.contrib import admin
from .models import CustomUser, UserProfile

# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = [
        "username", "email", "date_of_birth", "accept_tos", "last_password_change"
    ]

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        "user"
    ]
