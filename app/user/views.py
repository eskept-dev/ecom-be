from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from app.user import serializers
from app.user.models import User


class UserModelViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'put', 'delete']
    
    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['put'], url_path='change_password')
    def change_password(self, request):
        serializer = serializers.ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'Password changed successfully'},
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    @action(detail=False, methods=['get'], url_path='me')
    def get_me(self, request):
        return Response(
            serializers.UserSerializer(request.user).data, 
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=['get', 'put'], url_path='user_profile')
    def get_profile(self, request):
        if request.method == 'GET':
            return self.get_object(request)
        elif request.method == 'PUT':
            return self.update_profile(request)

    def get_object(self, request):
        return Response(
            serializers.UserProfileSerializer(request.user.userprofile).data, 
            status=status.HTTP_200_OK,
        )

    def update_profile(self, request):
        serializer = serializers.UserProfileSerializer(
            data=request.data,
            instance=request.user.userprofile,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializers.UserProfileSerializer(request.user.userprofile).data, 
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=False, methods=['get', 'put'], url_path='business_profile')
    def get_business_profile(self, request):
        if not request.user.is_business:
            return Response(
                {'error': 'User is not a business'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.method == 'GET':
            return self.get_business_object(request)
        elif request.method == 'PUT':
            return self.update_business_profile(request)

    def get_business_object(self, request):
        return Response(
            serializers.BusinessProfileSerializer(request.user.businessprofile).data, 
            status=status.HTTP_200_OK,
        )
    
    def update_business_profile(self, request):
        serializer = serializers.BusinessProfileSerializer(
            data=request.data,
            instance=request.user.businessprofile,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializers.BusinessProfileSerializer(request.user.businessprofile).data, 
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST,
        )
