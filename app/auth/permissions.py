from rest_framework.permissions import BasePermission


class IsInternalUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_internal


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_admin
    
    
class IsStaffUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff
