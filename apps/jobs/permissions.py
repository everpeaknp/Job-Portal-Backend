from rest_framework import permissions





class CanCreateJob(permissions.BasePermission):

    """Only customers (employers) and admins can publish job listings."""



    message = 'Only employers can create job listings.'



    def has_permission(self, request, view):

        user = request.user

        if not user or not user.is_authenticated:

            return False

        return getattr(user, 'role', None) in ('customer', 'admin')

