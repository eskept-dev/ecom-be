from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from app.auth import serializers
from app.user.models import User


class SignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = serializers.SignUpSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(serializers.SignUpSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivateUserView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        serializer = serializers.ActivationCodeSerializer(data=request.query_params)
        if not  serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.filter(
            activation_code=serializer.validated_data['activation_code']
        ).first()
        if not user:
            return Response(
                {'error': 'Invalid activation code'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.is_active:
            user.activate()
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class SignInView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = serializers.SignInSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response(serializers.SignInResponseSerializer({
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
            }).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendSignInEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = serializers.SendSignInEmailSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = serializers.RefreshTokenSerializer(data=request.data)
        if serializer.is_valid():
            refresh = RefreshToken(serializer.validated_data['refresh_token'])
            return Response({
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
