from datetime import timedelta
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework_simplejwt.tokens import Token

class ResetToken(Token):
    token_type = "reset"
    lifetime = timedelta(days=1)

def generate_reset_token(user):
    # set up token
    token = ResetToken.for_user(user)
    token.token_type = 'reset'

    return token

def send_reset_email(user):
    token = generate_reset_token(user)
    print(token)

    res = send_mail(
        'Password Reset',
        f'We have received a request to reset your account\'s password. The token to include with your password change request is \n\n{token}\n\nThe given token will expire 1 day after it is issued, If you did not send this request, please ignore this email.',
        settings.EMAIL_HOST_USER,
        [user.email]
    )

    return res == 1
