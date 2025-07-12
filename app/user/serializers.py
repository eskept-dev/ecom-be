from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from app.user.models import (
    User, UserProfile, BusinessProfile, PhoneNumberChannels,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['groups', 'user_permissions']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class ActivationCodeSerializer(serializers.Serializer):
    activation_code = serializers.CharField(write_only=True)

    def validate(self, attrs):
        activation_code = attrs.get('activation_code')
        if not activation_code:
            raise serializers.ValidationError('Activation code is required.')
        return attrs
    
    def save(self, **kwargs):
        user = User.objects.get(activation_code=self.validated_data['activation_code'])
        user.activate()
        return user


class LoginSerializer(serializers.Serializer):
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


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if not self.context['request'].user.check_password(attrs['old_password']):
            raise serializers.ValidationError('Old password is incorrect.')
        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()


class UserProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        source='user',
        read_only=True
    )
    available_on = serializers.MultipleChoiceField(
        choices=PhoneNumberChannels.choices,
        required=False,
        allow_empty=True
    )

    class Meta:
        model = UserProfile
        fields = [
            'id', 'user_id', 'avatar_url', 
            'first_name', 'last_name', 'full_name',
            'phone_number', 'available_on', 'date_of_birth',
            'gender', 'nationality'
        ]
        extra_kwargs = {
            'id': {'read_only': True},
            'user_id': {'read_only': True}
        }

    def create(self, validated_data):
        user = self.context['request'].user
        user_profile = UserProfile.objects.create(user=user, **validated_data)
        return user_profile

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class BusinessProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        source='user',
        read_only=True
    )
    available_on = serializers.MultipleChoiceField(
        choices=PhoneNumberChannels.choices,
        required=False,
        allow_empty=True
    )
    
    class Meta:
        model = BusinessProfile
        fields = [
            'id', 'user_id', 'name', 'tax_id', 'address',
            'contact_phone_number', 'available_on', 'contact_email',
            'website', 'logo_url', 'description', 'nationality',
            'representative_profile'
        ]
        extra_kwargs = {
            'id': {'read_only': True},
            'user_id': {'read_only': True}
        }
    
    def create(self, validated_data):
        user = self.context['request'].user
        business_profile = BusinessProfile.objects.create(user=user, **validated_data)
        return business_profile
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)



# ===============================
# Customer
# ===============================

class CustomerSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer(read_only=True)
    business_profile = BusinessProfileSerializer(read_only=True)

    class Meta:
        model = User
        exclude = ['groups', 'user_permissions']
        extra_kwargs = {
            'password': {'write_only': True}
        }
