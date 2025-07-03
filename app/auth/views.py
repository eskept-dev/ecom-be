from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from app.auth import serializers
from app.auth import services as auth_services
from app.auth import tasks as auth_tasks
from app.auth.enums import VerificationTypeEnum
from app.user.models import User


# ===============================
# Sign Up
# ===============================
class SignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if email and User.objects.filter(email=email).exists():
            return Response(
                {"error": "User with this email already exists."},
                status=status.HTTP_409_CONFLICT
            )

        serializer = serializers.SignUpSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()

        auth_tasks.send_verification_email_for_sign_up_task.apply_async(
            kwargs={'user_id': user.id}
        )

        return Response(serializers.SignUpSerializer(user).data, status=status.HTTP_201_CREATED)


class ResendVerificationEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = serializers.ResendVerificationEmailSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=serializer.validated_data['email']).first()
        if not user:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_400_BAD_REQUEST
            )

        verification_type = serializer.validated_data['verification_type']
        if verification_type == VerificationTypeEnum.SIGN_UP.value:
            return self.resend_sign_up_verification_email(user)

        return Response(
            {'error': 'Unsupported verification type'},
            status=status.HTTP_400_BAD_REQUEST
        )
        
    def resend_sign_up_verification_email(self, user: User):
        if user.is_active:
            return Response(
                {'error': 'User already verified'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.renew_activation_code()

        auth_tasks.send_verification_email_for_sign_up_task.apply_async(
            kwargs={'user_id': user.id}
        )

        return Response(
            {'message': 'Verification email sent'},
            status=status.HTTP_200_OK
        )


class ActivateUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = serializers.ActivationCodeSerializer(data=request.data)
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

        user.activate()

        return Response(
            {'message': 'User activated successfully'},
            status=status.HTTP_200_OK
        )


# ===============================
# Sign In
# ===============================
class CanSignInByPasswordView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        email = request.query_params.get('email')
        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        user = User.objects.filter(email=email).first()
        if not user:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {'can_sign_in_by_password': user.can_sign_in_by_password},
            status=status.HTTP_200_OK
        )


class SignInView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = serializers.SignInSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response(serializers.SignInResponseSerializer({
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
        }).data)


class SendSignInEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = serializers.SendSignInEmailSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        redirect_to = serializer.validated_data.get('redirect_to')

        user = User.objects.filter(email=email).first()
        if not user:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.is_active:
            auth_tasks.send_sign_in_email_task.apply_async(
                kwargs={'user_id': user.id, 'redirect_to': redirect_to}
            )
        else:
            user.renew_activation_code()
            auth_tasks.send_verification_email_for_sign_up_task.apply_async(
                kwargs={'user_id': user.id, 'redirect_to': redirect_to}
            )

        return Response(
            {'message': 'Sign in email sent'},
            status=status.HTTP_200_OK
        )


# ===============================
# Token
# ===============================
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


class GetPairsTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        refresh = RefreshToken.for_user(request.user)
        return Response({
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
        })


# ===============================
# Reset Password
# ===============================
class SendResetPasswordEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = serializers.SendResetPasswordEmailSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=serializer.validated_data['email']).first()
        if not user:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_400_BAD_REQUEST
            )

        auth_tasks.send_reset_password_email_task.apply_async(
            kwargs={'user_id': user.id}
        )

        return Response(
            {'message': 'Reset password email sent'},
            status=status.HTTP_200_OK
        )


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = serializers.ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        auth_services.reset_password(
            user=request.user,
            password=serializer.validated_data['password']
        )

        return Response(
            {'message': 'Password reset successfully'},
            status=status.HTTP_200_OK
        )
