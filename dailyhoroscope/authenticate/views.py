from datetime import datetime
from django.conf import settings
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import render
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from .authentication import PASSWORD_CHANGED_ERROR_MESSAGE
from .models import CustomUser
from .verifier import RegisterVerifier

REFRESH_TOKEN_EXPIRED_MESSAGE = 'Refresh token has expired. Please login again.'

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

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
                {'Invalid': error},
                status=status.HTTP_400_BAD_REQUEST
            )
        except IntegrityError as error:
            user.delete()
            return Response(
                {'Invalid': str(error.__cause__).split('  ')[1][:-1]},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.save()
        return Response(
            data={'Accepted': 'New user registered', 'data': user.serialize()}
        )

# log into an existing user account
class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username', None)
        password = request.data.get('password', None)
        user = authenticate(username=username, password=password)
        if user is None:
            return Response(
                {"Invalid": "Invalid email or password."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if not user.is_active:
            return Response(
                {"Invalid": "This account is inactive."},
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
            "Success": "Login successful.",
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
                {"Invalid": "Invalid token submitted."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # verify token, get user, and generate new tokens
        token = RefreshToken(raw_token)
        issue_date = datetime.fromtimestamp(token['iat'], tz=timezone.utc)
        expire_date = datetime.fromtimestamp(token['exp'], tz=timezone.utc)
        if expire_date > timezone.now():
            return Response(
                {'Invalid': REFRESH_TOKEN_EXPIRED_MESSAGE},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # TODO: blacklist here
        jwt = JWTAuthentication()
        user = jwt.get_user(token)
        if issue_date < user.last_password_change:
            return Response(
                {'Invalid': PASSWORD_CHANGED_ERROR_MESSAGE},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        data = get_tokens_for_user(user)

        # re-set the cookie to new refresh token, and return both tokens
        response = Response(
            {"Success": "Tokens refreshed.", 'data': data},
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
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(data=request.user.serialize())

class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        old_password = request.data['old_password']
        new_password = request.data['new_password']
        user = request.user
        if user is None:
            return Response(
                {'Invalid', 'User is not authenticated.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.check_password(old_password):
            return Response(
                {'Invalid': 'Entered incorrect password. Password change denied.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.last_password_change = timezone.now()
        user.save()
        
        data = get_tokens_for_user(user)

        # re-set the cookie to new refresh token, and return both tokens
        response = Response(
            {"Success": "Password changed successfully.", 'data': data},
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
        
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        response = Response(
            {'Success': 'Successfully logged out.'},
            status=status.HTTP_200_OK,
        )
        response.set_cookie(
            key=settings.SIMPLE_JWT['AUTH_COOKIE'],
            value='',
            max_age=1,
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
            path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH'],        )
        return response