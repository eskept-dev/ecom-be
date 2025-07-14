from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter

from django_filters.rest_framework import DjangoFilterBackend

from app.auth.permissions import IsInternalUser
from app.base.mixins import SoftDeleteViewSetMixin
from app.booking.models import Booking
from app.booking.serializers import CustomerBookingSerializer
from app.user import serializers
from app.user.models import User, UserRole
from app.user.serializers import UserProfileSerializer
from app.base.pagination import CustomPagination


class UserModelViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'delete']
    
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


class InternalUserModelViewSet(ModelViewSet):
    queryset = User.objects.filter(role__in=[UserRole.ADMIN, UserRole.STAFF])
    serializer_class = serializers.UserSerializer
    permission_classes = [IsInternalUser]


class CustomerModelViewSet(ModelViewSet, SoftDeleteViewSetMixin):
    queryset = User.objects.filter(role__in=[UserRole.CUSTOMER, UserRole.BUSINESS], is_deleted=False)
    serializer_class = serializers.CustomerSerializer
    permission_classes = [IsInternalUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["id", "email"]
    ordering_fields = ["id", "email", "role", "status"]
    ordering = ["-id"]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.CustomerListingSerializer
        return serializers.CustomerSerializer
    
    def filter_queryset(self, queryset):
        if self.action == 'get_bookings':
            return queryset
        return super().filter_queryset(queryset)

    @action(detail=True, methods=['get'], url_path='bookings')
    def get_bookings(self, request, *args, **kwargs):
        query_params = request.query_params
        
        bookings_query = Booking.objects.filter(customer=self.get_object())

        if query_params.get('search'):
            search_query = query_params.get('search')
            bookings_query = bookings_query.filter(code__icontains=search_query)
            
        if query_params.get('ordering'):
            bookings_query = bookings_query.order_by(query_params.get('ordering'))

        paginator = CustomPagination()
        page = paginator.paginate_queryset(bookings_query, request)
        if page is not None:
            serializer = CustomerBookingSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = CustomerBookingSerializer(bookings_query, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='profile')
    def get_profile(self, request, *args, **kwargs):
        customer = self.get_object()

        return Response(
            serializers.CustomerSerializer(customer).data, 
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=['patch'], url_path='user_profile')
    def update_partial_user_profile(self, request, *args, **kwargs):
        customer = self.get_object()
        serializer = UserProfileSerializer(
            data=request.data,
            instance=customer.userprofile,
            partial=True
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()
        return Response(
            serializers.UserProfileSerializer(customer.userprofile).data, 
            status=status.HTTP_200_OK,
        )
