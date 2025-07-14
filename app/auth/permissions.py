from rest_framework.permissions import BasePermission


class IsInternalUser(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.is_internal
        return False


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.is_admin
        return False
    
    
class IsStaffUser(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.is_staff
        return False
