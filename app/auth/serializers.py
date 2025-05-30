from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken


from app.auth.enums import VerificationTypeEnum
from app.user.models import User


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
    verification_type = serializers.ChoiceField(choices=VerificationTypeEnum.choices())

    def validate(self, attrs):
        email = attrs.get('email')
        if not email:
            raise serializers.ValidationError('Email is required.')
        
        user = User.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError('User not found.')
        
        return attrs


class ActivationCodeSerializer(serializers.Serializer):
    activation_code = serializers.CharField(write_only=True)

    def validate(self, attrs):
        activation_code = attrs.get('activation_code')
        if not activation_code:
            raise serializers.ValidationError('Activation code is required.')
        return attrs


class SignInSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
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

    def validate(self, attrs):
        email = attrs.get('email')
        if not email:
            raise serializers.ValidationError('Email is required.')
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
