import datetime
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils import timezone
import re
from .models import CustomUser

USERNAME_PATTERN = r'^[a-zA-Z0-9_]+$'
PASSWORD_PATTERN = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[\W_]).*$'

class RegisterVerifier:
    def __init__(self, data):
        self._data = data
        self._errors = []
    
    def verify(self):
        # always check if keys exist
        self.verify_exists('email')
        self.verify_exists('username')
        self.verify_exists('password')
        self.verify_exists('date_of_birth')
        self.verify_exists('accept_tos')

        # should be done beforehand
        self.verify_length('email', 3, 255)             # DataError - may as well verify here
        self.verify_username('username')
        self.verify_length('username', 3, 255)          # DataError - may as well verify here
        self.verify_length('password', 8, 255)          # will be hashed so verify now
        self.verify_password('password')
        self.verify_age('date_of_birth')
        self.verify_true_or_false('accept_tos')         # could be anything else
        
        # can be done by model but done here since I already did the work :)
        self.verify_date('date_of_birth')               # ValidationError
        self.verify_email('email')                      # ValidationError
        self.verify_email_not_exists('email')           # IntegrityError
        self.verify_username_not_exists('username')     # IntegrityError
        
        return len(self._errors) == 0
    
    def errors(self):
        return self._errors

    def has_errors(self):
        return len(self._errors) > 0

    def verify_exists(self, key):
        if key not in self._data:
            self._errors.append(f'{key} field must not be empty.')
            return False
        return True
    
    def verify_date(self, key):
        if key not in self._data:
            return
        date = self._data[key]
        try:
            datetime.date.fromisoformat(date)
        except ValueError:
            self._errors.append(f'{key} field must contain a valid Date in format "YYYY-MM-DD".')
    
    def verify_email(self, key):
        if key not in self._data:
            return
        val = self._data[key]
        try:
            validate_email(val)
        except ValidationError:
            self._errors.append(f'{key} field must be a valid email address.')

    def verify_username(self, key):
        if key not in self._data:
            return
        val = self._data[key]
        if re.match(pattern=USERNAME_PATTERN, string=val) is None:
            self._errors.append(f'{key} must consist of only letters, numbers, and underscores.')
    
    def verify_password(self, key):
        if key not in self._data:
            return
        val = self._data[key]
        if re.match(pattern=PASSWORD_PATTERN, string=val) is None:
            self._errors.append(f'{key} must contain at least one lowercase letter, one uppercase letter, one digit, and one special character.')
    
    def verify_email_not_exists(self, key):
        if key not in self._data:
            return
        val = self._data[key]
        if CustomUser.objects.filter(email=val).exists():
            self._errors.append('A user with the given email already exists.')
    
    def verify_username_not_exists(self, key):
        if key not in self._data:
            return
        val = self._data[key]
        if CustomUser.objects.filter(username=val).exists():
            self._errors.append('A user with the given username already exists.')
    
    def verify_true_or_false(self, key):
        if key not in self._data:
            return
        val = self._data[key]
        if val != "TRUE" and val != "FALSE":
            self._errors.append(f'{key} field must be either "TRUE" or "FALSE".')
    
    def verify_length(self, key, min, max):
        if key not in self._data:
            return
        val = self._data[key]
        if len(val) < min:
            self._errors.append(f'{key} field must have a length greater than or equal to {min}.')
        elif len(val) > max:
            self._errors.append(f'{key} field must have a length less than or equal to {max}.')
    
    def verify_age(self, key):
        if key not in self._data:
            return
        try:
            date = datetime.date.fromisoformat(self._data[key])
            today = timezone.now().date()
            age = int((today-date).days / 365.25)
            if age < 13:
                self._errors.append('Age must be greater than or equal to 13.')
        except ValueError:
            return
