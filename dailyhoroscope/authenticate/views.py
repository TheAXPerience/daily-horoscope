import datetime
from django.conf import settings
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.html import escape
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from .authentication import PASSWORD_CHANGED_ERROR_MESSAGE
from .email import send_reset_email, ResetToken
from .models import CustomUser
from .verifier import RegisterVerifier

REFRESH_TOKEN_EXPIRED_MESSAGE = 'Refresh token has expired. Please login again.'

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    # print(datetime.fromtimestamp(refresh['exp'], tz=timezone.utc))
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# register new user
class RegisterView(APIView):
    def post(self, request):
        data = request.data

        # parse errors from missing data
        verifier = RegisterVerifier(data)
        if not verifier.verify():
            return Response(
                {'message': verifier.errors()},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # create and save new user
        try:
            user = CustomUser.objects.create(
                email=data['email'],
                username=data['username'],
                date_of_birth=data['date_of_birth'],
                accept_tos=(data['accept_tos'] == "TRUE")
            )
            user.set_password(data['password'])
            user.full_clean()
        except ValidationError as error:
            user.delete()
            return Response(
                {'message': error},
                status=status.HTTP_400_BAD_REQUEST
            )
        except IntegrityError as error:
            user.delete()
            return Response(
                {'message': str(error.__cause__).split('  ')[1][:-1]},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.save()
        return Response(
            data={'message': 'New user registered.', 'data': user.serialize()}
        )

# log into an existing user account
class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username', None)
        password = request.data.get('password', None)
        user = authenticate(username=username, password=password)
        if user is None:
            return Response(
                {"message": "Invalid email or password."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if not user.is_active:
            return Response(
                {"message": "This account is inactive."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        response = Response()
        data = get_tokens_for_user(user)
        response.set_cookie(
            key=settings.SIMPLE_JWT['AUTH_COOKIE'],
            value=data['refresh'],
            expires=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
            path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH'],
        )
        response.data = {
            "message": "Login successful.",
            "data": data
        }
        return response

# refresh tokens, must have refresh token in cookies (meaning must've logged in before)
class RefreshView(APIView):
    def post(self, request):
        # find raw refresh token in cookies; else invalid
        raw_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE']) or None
        if raw_token is None:
            return Response(
                {"message": "Invalid token submitted."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # verify token, get user, and generate new tokens
        token = RefreshToken(raw_token)
        issue_date = datetime.datetime.fromtimestamp(token['iat'], tz=datetime.timezone.utc)
        expire_date = datetime.datetime.fromtimestamp(token['exp'], tz=datetime.timezone.utc)
        if expire_date < timezone.now():
            return Response(
                {'message': REFRESH_TOKEN_EXPIRED_MESSAGE},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # TODO: blacklist here
        jwt = JWTAuthentication()
        user = jwt.get_user(token)
        if issue_date < user.last_password_change:
            return Response(
                {'message': PASSWORD_CHANGED_ERROR_MESSAGE},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        data = get_tokens_for_user(user)

        # re-set the cookie to new refresh token, and return both tokens
        response = Response(
            {"message": "Tokens refreshed.", 'data': data},
            status=status.HTTP_200_OK,
        )
        response.set_cookie(
            key=settings.SIMPLE_JWT['AUTH_COOKIE'],
            value=data['refresh'],
            expires=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
            path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH'],
        )
        return response

# retrieve user information
class UserView(APIView):
    def get_or_404(self, username):
        return get_object_or_404(CustomUser, username=username)

    def get(self, request, username):
        user = self.get_or_404(username)
        if user is None:
            return Response(
                data={'message': 'A user with the given username could not be found'},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(data=user.profile.serialize())

class ProfileChangesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        context = {
            "description": profile.description,
            "dob_public": profile.dob_public,
            "email_public": profile.email_public,
            "subscribed_to_newsletter": profile.subscribed_to_newsletter
        }
        return Response(context)
    
    def put(self, request):
        profile = request.user.profile
        if "description" in request.data:
            profile.description = escape(request.data["description"])
        if "dob_public" in request.data:
            profile.dob_public = request.data["dob_public"]
        if "email_public" in request.data:
            profile.email_public = request.data["email_public"]
        if "subscribed_to_newsletter" in request.data:
            profile.subscribed_to_newsletter = request.data["subscribed_to_newsletter"]
        profile.save()
        return Response(
            {'message': 'User\'s profile settings have been updated.'},
            status=status.HTTP_202_ACCEPTED
        )

    def patch(self, request, *args, **kwargs):
        return self.put(request, *args, **kwargs)
    
    def delete(self, request):
        try:
            request.user.delete()
            return Response(
                {'message': 'User successfully deleted.'}, 
                status=status.HTTP_202_ACCEPTED
            )
        except:
            return Response(
                {'message': 'Error trying to delete the current user.'},
                status=status.HTTP_400_BAD_REQUEST
            )

class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        old_password = request.data['old_password'] if 'old_password' in request.data else None
        new_password = request.data['new_password'] if 'new_password' in request.data else None
        if old_password is None or new_password is None:
            return Response(
                {'message': 'Incorrect/missing data submitted.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user = request.user
        if user is None:
            return Response(
                {'message', 'User is not authenticated.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.check_password(old_password):
            return Response(
                {'message': 'Entered incorrect password. Password change denied.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        verifier = RegisterVerifier({'password': new_password})
        verifier.verify_password('password')
        if verifier.has_errors():
            return Response(
                {'message': verifier.errors()[0]},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.last_password_change = timezone.now()
        user.save()
        
        data = get_tokens_for_user(user)

        # re-set the cookie to new refresh token, and return both tokens
        response = Response(
            {"message": "Password changed successfully.", 'data': data},
            status=status.HTTP_202_ACCEPTED,
        )
        response.set_cookie(
            key=settings.SIMPLE_JWT['AUTH_COOKIE'],
            value=data['refresh'],
            expires=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
            path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH'],
        )
        return response

class ResetPasswordRequestView(APIView):
    def post(self, request):
        if 'email' not in request.data or 'date_of_birth' not in request.data:
            return Response(
                data={'message': 'The "email" and "date_of_birth" fields must be included.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = get_object_or_404(CustomUser, email=request.data['email'])
        dob = datetime.date.fromisoformat(request.data['date_of_birth'])
        if (dob != user.date_of_birth):
            return Response(
                data={'message': 'The given date of birth is incorrect for the account with the given email address.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        send_reset_email(user)

        return Response(
            {'message': 'Password reset email has been sent.'},
            status=status.HTTP_200_OK
        )

class ResetPasswordView(APIView):
    def post(self, request):
        if 'password' not in request.data or 'token' not in request.data:
            return Response(
                {'message': 'Invalid password reset request.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        token = ResetToken(request.data['token'])
        expire_date = datetime.datetime.fromtimestamp(token['exp'], tz=datetime.timezone.utc)
        if expire_date < timezone.now():
            return Response(
                {'message': 'The token has passed its expiration date.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        
        new_password = request.data['password']
        verifier = RegisterVerifier({'password': new_password})
        verifier.verify_password('password')
        if verifier.has_errors():
            return Response(
                {'message': verifier.errors()[0]},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        jwt = JWTAuthentication()
        user = jwt.get_user(token)

        user.set_password(new_password)
        user.last_password_change = timezone.now()
        user.save()

        return Response(
            {'message': 'Password changed successfully.'},
            status=status.HTTP_202_ACCEPTED
        )

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE']) or None
        if token is None:
            return Response(
                {"message": "User already logged out."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        response = Response(
            {'message': 'Successfully logged out.'},
            status=status.HTTP_200_OK,
        )
        response.set_cookie(
            key=settings.SIMPLE_JWT['AUTH_COOKIE'],
            value='',
            max_age=1,
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
            path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH'],
        )
        return response

class TermsOfServiceView(APIView):
    def get(self, request):
        from .termsofservice import TERMS_OF_SERVICE
        return Response(TERMS_OF_SERVICE)
