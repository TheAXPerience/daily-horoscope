import datetime
from django.shortcuts import get_object_or_404, render
from django.utils.html import escape
from rest_framework import permissions, status 
from rest_framework.response import Response
from rest_framework.views import APIView
from authenticate.models import CustomUser
from .models import Horoscope, DailyHoroscope, ReportHoroscope

# Create your views here.

# POST: create horoscope
class HoroscopeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        
        if "horoscope" not in request.data:
            return Response(
                data={'message', 'Request did not contain a "horoscope" field.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        txt = escape(request.data["horoscope"])
        horoscope = Horoscope(poster=user, horoscope=txt)
        horoscope.save()
        return Response(
            data={
                'message': 'Horoscope has been successfully uploaded',
                'data': horoscope.serialize(),
            }, status=status.HTTP_201_CREATED,
        )


# GET: read a singular horoscope
# PUT/PATCH: update horoscope
# DELETE: delete horoscope
class SingularHoroscopeView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_or_404(self, hid):
        return get_object_or_404(Horoscope, id=hid)

    def get(self, request, hid):
        horoscope = self.get_or_404(hid)
        return Response(data=horoscope.serialize())

    def put(self, request, hid):
        horoscope = self.get_or_404(hid)
        if request.user != horoscope.poster:
            return Response(
                data={
                    'message': 'The current logged-in user does not have the permissions to change another user\'s horoscopes.'
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        if "horoscope" not in request.data:
            return Response(
                data={
                    'message': 'No data found in the request to replace.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        horoscope.horoscope = escape(request.data["horoscope"])
        horoscope.save()
        return Response(
            data={
                'message': f'Horoscope #{hid} successfully changed.',
                'data': horoscope.serialize()
            },
            status=status.HTTP_202_ACCEPTED,
        )

    def patch(self, request, hid):
        return self.put(request, hid)

    def delete(self, request, hid):
        horoscope = self.get_or_404(hid)
        if request.user != horoscope.poster:
            return Response(
                data={
                    'message': 'The current logged-in user does not have the permissions to delete another user\'s horoscopes.'
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            horoscope.delete()
            return Response(
                data={'message': 'Horoscope successfully deleted.'},
                status=status.HTTP_200_OK,
            )
        except:
            return Response(
                data={'message': 'An error has occurred.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

# GET: daily horoscopes (of a given day)
class DailyHoroscopeView(APIView):
    def get_most_recent(self):
        return DailyHoroscope.objects.latest('date')
    
    def get(self, request):
        # NOTE: if date is None, use current date
        date = request.GET.get('date', None)
        if date is None:
            return Response(self.get_most_recent().serialize())
        try:
            daily_date = datetime.date.fromisoformat(date)
        except:
            return Response(
                data={'message': 'URL must contain a valid Date in format "YYYY-MM-DD".'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        horoscopes = get_object_or_404(DailyHoroscope, date=daily_date)
        return Response(
            data=horoscopes.serialize()
        )


# GET: all horoscopes (paginated) of a user
class UserHoroscopeView(APIView):
    def get_or_404(self, username):
        return get_object_or_404(CustomUser, username=username)

    def get(self, request, username):
        user = self.get_or_404(username)
        if user is None:
            return Response(
                data={'message': f'The user "{username}" could not be found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        horoscopes = user.horoscopes_written.order_by('-date_updated')
        context = []
        for horoscope in horoscopes:
            context.append(horoscope.serialize())
        return Response(context)

# POST: report a horoscope for inappropriate content
class ReportHoroscopeView(APIView):
    def post(self, request, hid):
        horoscope = get_object_or_404(Horoscope, id=hid)
        if "reason" not in request.data:
            return Response(
                data={'message': 'The "reason" field must be filled out to submit a valid report.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        report = ReportHoroscope(
            reported_horoscope=horoscope, 
            reason=escape(request.data["reason"]),
            reviewed=False
        )
        report.save()
        return Response(
            data={'message': 'Report has been submitted. Thank you for your time and consideration.'},
            status=status.HTTP_202_ACCEPTED,
        )
