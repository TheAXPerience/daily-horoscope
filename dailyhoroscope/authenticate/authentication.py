import datetime
from django.utils import timezone
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

PASSWORD_CHANGED_ERROR_MESSAGE = 'Password has been changed. Please login again.'

class CustomAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None
        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None
        
        validated_token = self.get_validated_token(raw_token)
        user = self.get_user(validated_token)

        # add a second to take into account milliseconds being stored in the database value
        # i do not know how else to deal with this
        issue_date = datetime.datetime.fromtimestamp(validated_token['iat'], tz=datetime.timezone.utc) + timezone.timedelta(seconds=1)
        if issue_date < user.last_password_change:
            # functionality: error if issue date is before last password change
            raise AuthenticationFailed(PASSWORD_CHANGED_ERROR_MESSAGE)

        return user, validated_token
