from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

# Create your models here.
class UserManager(BaseUserManager):
    use_in_migration = True

    def create_user(self, email, username, password=None, date_of_birth=None, accept_tos=False):
        if not email:
            raise ValueError('Email is required')
        elif not username:
            raise ValueError('Username is required')
        
        user = self.model(
            username=username,
            email=email,
            date_of_birth=date_of_birth,
            accept_tos=accept_tos
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, password=None, date_of_birth=None, accept_tos=False):
        user = self.create_user(email, username, password, date_of_birth, accept_tos)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractUser):
    username = models.CharField(max_length=255, unique=True, null=False)
    email = models.EmailField(max_length=255, unique=True, null=False)
    date_of_birth = models.DateField(null=True)
    accept_tos = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True) # set to False when doing account activation
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    last_password_change = models.DateTimeField(default=timezone.now)

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def serialize(self):
        ans = {
            "username": self.username,
            "email": self.email,
            "date_of_birth": self.date_of_birth
        }
        return ans
