from rest_framework.response import Response
from rest_framework import serializers, status
from django.contrib.auth import get_user_model
from .models import *


class UserRegistrationSerializer(serializers.ModelSerializer):
    password_confirmation = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'name', 'college', 'year', 'password', 'password_confirmation']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirmation']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        # Remove the password_confirmation from the validated data since it's not needed for user creation
        validated_data.pop('password_confirmation', None)

        # Create the user instance
        user = User(
            email=validated_data['email'],
            name=validated_data['name'],
            college=validated_data['college'],
            year=validated_data['year']
        )

        user.set_password(validated_data['password'])
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'name', 'college', 'year']


class BroadCastSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=50)
    message = serializers.CharField(max_length=100)


class VerifyAccountSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=4)


class EmailSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=100)


class OtpPasswordSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=100)
    otp = serializers.IntegerField()
    password1 = serializers.CharField(max_length=100)
    password2 = serializers.CharField(max_length=100)


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['college', 'username', 'year', 'phone_number']

class UserQuerySerializer(serializers.ModelSerializer):

    class Meta:
        model = UserQueries
        fields = ['name','email','question']