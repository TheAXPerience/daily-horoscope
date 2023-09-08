import datetime
from .models import CustomUser

class RegisterVerifier:
    def __init__(self, data):
        self._data = data
        self._errors = []
    
    def verify(self):
        self.verify_exists('email')
        self.verify_exists('username')
        self.verify_exists('password')
        self.verify_exists('date_of_birth')
        self.verify_exists('accept_tos')
        self.verify_date('date_of_birth')
        self.verify_email_not_exists('email')
        self.verify_username_not_exists('username')
        self.verify_true_or_false('accept_tos')
        return len(self._errors) == 0
    
    def errors(self):
        return self._errors

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
            self._errors.append(f'{key} field must contains a valid Date in format "YYYY-MM-DD".')
    
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
