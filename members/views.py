import random
from django.core.mail import send_mail
from rest_framework_simplejwt.authentication import JWTAuthentication
from members.serializers import UserRegistrationSerializer, BroadCastSerializer
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import *
from .serializers import UserSerializer, VerifyAccountSerializer, OtpPasswordSerializer, EmailSerializer, \
    UserUpdateSerializer, UserLoginSerializer
from .utils import send_email_to_user, send_otp
import pandas as pd
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
import uuid
from django.core.exceptions import ObjectDoesNotExist


class UserRegistrationAPIView(APIView):
    serializer_class = UserRegistrationSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)

    def get(self, request):
        content = {'message': 'Hello!'}
        return Response(content)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            if serializer.validated_data['password'] != serializer.validated_data['password_confirmation']:
                return Response('Passwords do not match', status=status.HTTP_400_BAD_REQUEST)
            phone = serializer.validated_data['phone_number']
            if len(phone) != 10:
                return Response('Enter 10 digit phone number', status=status.HTTP_400_BAD_REQUEST)
            if not phone.isnumeric():
                return Response('Please enter a valid phone number', status=status.HTTP_400_BAD_REQUEST)

            user = serializer.save()
            if user.is_active:
                # Generate JWT token
                refresh = RefreshToken.for_user(user)
                token = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
                return Response({'token': token, 'username': user.email}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = VerifyAccountSerializer

    def get(self, request):
        # Generate a new OTP and send it in the response
        user = request.user
        otp = str(random.randint(1000, 9999))  # Generate a 6-digit OTP

        # Save the OTP to the user model (you might have a field for it)
        user.otp = otp
        user.save()

        # Send email with OTP
        send_email_to_user(user.email, "Email Verification", f'Your OTP is: {otp}')

        return Response({'message': 'Email sent for verification.', 'otp': otp}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = request.user
            otp = serializer.validated_data['otp']

            if user.otp != otp:
                return Response({'message': 'Wrong OTP entered'}, status=status.HTTP_400_BAD_REQUEST)

            user.is_verified = True
            user.save()
            send_email_to_user(user.email, "Registration Successful",
                               "You've successfully registered and verified for EES")

            return Response({'message': 'Successfully Verified'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginAPIView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(email=serializer.validated_data['email'])
        password = serializer.validated_data['password']
        if not user:
            return Response("User does not exist")

        if not user.check_password(password):
            return Response("Wrong password")

        if not user.is_verified:
            return Response({'detail': 'Account not verified. Please verify your account.'},
                            status=status.HTTP_403_FORBIDDEN)

        if user.is_active:
            # Generate JWT token
            refresh = RefreshToken.for_user(user)
            token = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            return Response({'token': token, 'username': user.email}, status=status.HTTP_200_OK)

        return Response({'detail': 'User account is not active.'}, status=status.HTTP_403_FORBIDDEN)


class UserViewAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the authenticated user
        user = request.user

        # Serialize the user data
        serializer = UserSerializer(user, context={'request': request})  # Pass the request to include the context

        # Return the serialized user data
        return Response(serializer.data)


class UserLogoutViewAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"detail": "Logout successful."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ExportImportExcel(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request, format=None):
        user_objs = User.objects.all()
        serializer = UserSerializer(user_objs, many=True)
        df = pd.DataFrame(serializer.data)
        print(df)
        df.to_csv(f"C:/Users/Public/Documents/{uuid.uuid4()}.csv", encoding="UTF-8")

        return Response({'status': 200})


class BroadCastViewAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    serializer_class = BroadCastSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            subject = serializer.validated_data['subject']
            for user in User.objects.all():
                email = user.email
                send_email_to_user(email, subject)

        response = Response()
        response.data = {
            'message': 'Something went wrong.'
        }
        return response


class ForgotPassword(APIView):
    serializer_class = EmailSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(email=serializer.data["email"])

            except ObjectDoesNotExist:
                return Response({"error": " Email does not exist"}, status=status.HTTP_404_NOT_FOUND)

            otp1 = send_otp(user.email, "Password Reset OTP")
            user.set_and_hash_otp(str(otp1))
            return Response({"Check Your Mail"})


class ChangePassword(APIView):
    serializer_class = OtpPasswordSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            try:
                user = User.objects.get(email=serializer.data["email"])

            except ObjectDoesNotExist:
                return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

            if not user.is_verified:
                return Response({'detail': 'Account not verified. Please verify your account.'},
                                status=status.HTTP_403_FORBIDDEN)

            # Retrieve the hashed OTP from the database and compare it
            if user.check_otp(serializer.data["otp"]):
                # OTP is correct, check and change the password
                if serializer.data["password1"] == serializer.data["password2"]:
                    user.set_password(serializer.data["password1"])
                    return Response({"success": "Password changed successfully"})

                return Response({"error": "Passwords do not match"})

            return Response({"error": "Wrong OTP entered"})


class UserUpdateAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        # Get the authenticated user
        user = request.user

        # Validate and update user data
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User information updated successfully.'})
        else:
            return Response(serializer.errors, status=400)
