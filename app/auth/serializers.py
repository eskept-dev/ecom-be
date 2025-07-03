from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken


from app.auth.enums import VerificationTypeEnum
from app.auth import services as auth_services
from app.user.models import User
from app.core.utils.url_path import format_url_path


# ===============================
# Sign Up
# ===============================
class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['groups', 'user_permissions']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False, 'allow_blank': True}
        }
        
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class ResendVerificationEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    redirect_to = serializers.CharField(required=False, allow_blank=True)
    verification_type = serializers.ChoiceField(choices=VerificationTypeEnum.choices())

    def validate(self, attrs):
        email = attrs.get('email')
        if not email:
            raise serializers.ValidationError('Email is required.')
        
        user = User.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError('User not found.')
        
        redirect_to = attrs.get('redirect_to')
        attrs['redirect_to'] = format_url_path(redirect_to)
        
        return attrs


class ActivationCodeSerializer(serializers.Serializer):
    activation_code = serializers.CharField(write_only=True)

    def validate(self, attrs):
        activation_code = attrs.get('activation_code')
        if not activation_code:
            raise serializers.ValidationError('Activation code is required.')
        return attrs


# ===============================
# Sign In
# ===============================
class SignInSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = auth_services.authenticate(email, password)
            if not user:
                raise serializers.ValidationError('User not found')
            if not user.is_active:
                raise serializers.ValidationError('User account is not activated')
        else:
            raise serializers.ValidationError('Must include "email" and "password"')

        attrs['user'] = user
        return attrs


class SignInResponseSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()


class SendSignInEmailSerializer(serializers.Serializer):    
    email = serializers.EmailField()
    redirect_to = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        email = attrs.get('email')
        if not email:
            raise serializers.ValidationError('Email is required.')

        redirect_to = attrs.get('redirect_to')
        attrs['redirect_to'] = format_url_path(redirect_to)

        return attrs


class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(write_only=True)

    def validate(self, attrs):
        refresh_token = attrs.get('refresh_token')
        if not refresh_token:
            raise serializers.ValidationError('Refresh token is required.')
        return attrs
    
    def save(self, **kwargs):
        refresh = RefreshToken(self.validated_data['refresh_token'])
        return {
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
        }


class VerifyEmailQuerySerializer(serializers.Serializer):
    email = serializers.EmailField()
    verification_type = serializers.ChoiceField(choices=VerificationTypeEnum.choices())


# ===============================
# Reset Password
# ===============================
class SendResetPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    redirect_to = serializers.CharField(required=False)

    def validate(self, attrs):
        email = attrs.get('email')
        if not email:
            raise serializers.ValidationError('Email is required.')
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        password = attrs.get('password')
        if not password:
            raise serializers.ValidationError('Password is required.')
        return attrs
