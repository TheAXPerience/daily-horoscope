from rest_framework import serializers
from .models import CustomUser
import datetime

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'password', 'date_of_birth', 'accept_tos']
    
    def create(self, data):
        user = CustomUser.objects.create(
            email=data['email'],
            username=data['username'],
            date_of_birth=data['date_of_birth'],
            accept_tos=data['accept_tos']
        )
        user.set_password(data['password'])
        user.save()
        return user
