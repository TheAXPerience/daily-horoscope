from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

DATEOFBIRTH_FORMAT = '%Y/%m/%d'

# Create your models here.
def get_sentinel_user():
    from django.contrib.auth import get_user_model
    return get_user_model().objects.get_or_create(
        email="deleted@deleted.deleted",
        username="deleted"
    )[0]

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
            "date_of_birth": self.date_of_birth.strftime(DATEOFBIRTH_FORMAT)
        }
        return ans

class UserProfile(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    # profile picture?
    description = models.TextField(null=True)
    dob_public = models.BooleanField(default=False)
    email_public = models.BooleanField(default=False)
    subscribed_to_newsletter = models.BooleanField(default=False)

    def serialize(self):
        ans = {
            "username": self.user.username,
            "description": self.description,
            "subscribed_to_newsletter": self.subscribed_to_newsletter,
        }
        if self.email_public:
            ans['email'] = self.user.email
        if self.dob_public:
            ans['date_of_birth'] = self.user.date_of_birth.strftime(DATEOFBIRTH_FORMAT)
        return ans
