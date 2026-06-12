from rest_framework import permissions


class CanCreateService(permissions.BasePermission):
    """Only taskers (and admins) can publish marketplace services."""

    message = 'Only taskers can create service listings.'

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return getattr(user, 'role', None) in ('tasker', 'admin')
