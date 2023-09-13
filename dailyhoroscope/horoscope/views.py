from datetime import datetime
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import render
from django.utils import timezone
from rest_framework import permissions, status 
from rest_framework.response import Response
from rest_framework.views import APIView

# Create your views here.

# POST: create horoscope
class HoroscopeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        pass

# GET: read a singular horoscope
# PUT/PATCH: update horoscope
# DELETE: delete horoscope
class SingularHoroscopeView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, hid):
        pass

    def put(self, request, hid):
        pass

    def patch(self, request, hid):
        return self.put(request, hid)

    def delete(self, request, hid):
        pass

# GET: daily horoscopes (of a given day)
class DailyHoroscopeView(APIView):
    def get(self, request, date=None):
        # NOTE: if date is None, use current date
        pass

# GET: all horoscopes (paginated) of a user
class HoroscopesOfUserView(APIView):
    def get(self, request, username):
        pass

# POST: report a horoscope for inappropriate content
class ReportHoroscope(APIView):
    def post(self, request, hid):
        pass
