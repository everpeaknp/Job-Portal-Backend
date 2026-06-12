from rest_framework import permissions


class CanCreateProject(permissions.BasePermission):
    """Only customers (employers) and admins can publish project listings."""

    message = 'Only employers can create project listings.'

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return getattr(user, 'role', None) in ('customer', 'admin')
