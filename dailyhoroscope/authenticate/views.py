from django.conf import settings
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import render
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from .models import CustomUser

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
        if 'email' not in data:
            return Response(
                {'Invalid': 'Email field must not be empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if 'username' not in data:
            return Response(
                {'Invalid': 'Username field must not be empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if 'password' not in data:
            return Response(
                {'Invalid': 'Password field must not be empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if 'date_of_birth' not in data:
            return Response(
                {'Invalid': 'Date of Birth field must not be empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if 'accept_tos' not in data:
            return Response(
                {'Invalid': 'Terms of Service Acceptance field must not be empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if data['accept_tos'] != "TRUE" and data['accept_tos'] != 'FALSE':
            return Response(
                {'Invalid': 'Terms of Service Acceptance field must be either "TRUE" or "FALSE"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # create and save new user
        try:
            user = CustomUser.objects.create(
                email=data['email'],
                username=data['username'],
                date_of_birth=data['date_of_birth'],
                accept_tos=(data['accept_tos'] == "TRUE")
            )
        except ValidationError as error:
            return Response(
                {'Invalid': error},
                status=status.HTTP_400_BAD_REQUEST
            )
        except IntegrityError as error:
            return Response(
                {'Invalid': str(error.__cause__).split('  ')[1][:-1]},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.set_password(data['password'])
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
        raw_token = request.COOKIES.get('refresh_token') or None
        if raw_token is None:
            return Response(
                {"Invalid": "Invalid token submitted."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # verify token, get user, and generate new tokens
        token = RefreshToken(raw_token)

        # TODO: blacklist here
        jwt = JWTAuthentication()
        user = jwt.get_user(token)
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