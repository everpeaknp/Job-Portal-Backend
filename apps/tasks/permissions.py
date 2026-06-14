"""
Custom permissions for Tasks app.
"""
from rest_framework import permissions

from .listing import LISTING_KIND_TASK


class IsTaskOwner(permissions.BasePermission):
    """
    Permission to only allow task owners to edit/delete tasks.
    """
    
    message = 'You must be the task owner to perform this action.'
    
    def has_object_permission(self, request, view, obj):
        """Check if user is the task owner."""
        return obj.owner == request.user


class IsTaskOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission to allow read-only access to everyone,
    but write access only to the task owner.
    """
    
    def has_object_permission(self, request, view, obj):
        """Check permissions."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user


class IsTaskOwnerOrAssignedTasker(permissions.BasePermission):
    """
    Permission for task owner or assigned tasker.
    """
    
    message = 'You must be the task owner or assigned tasker to perform this action.'
    
    def has_object_permission(self, request, view, obj):
        """Check if user is owner or assigned tasker."""
        return obj.owner == request.user or obj.assigned_tasker == request.user


class CanCreateTask(permissions.BasePermission):
    """
    Marketplace tasks: customers and taskers.
    Services: taskers only. Jobs/projects: customers only.
    """

    message = 'You do not have permission to create this listing.'

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if getattr(user, 'role', None) == 'admin':
            return True
        listing_kind = request.data.get('listing_kind') if hasattr(request.data, 'get') else None
        if listing_kind == 'service':
            return user.role == 'tasker'
        if listing_kind in (None, '', LISTING_KIND_TASK):
            return user.role in ('customer', 'tasker')
        if listing_kind in ('project', 'job'):
            return user.role == 'customer'
        return user.role == 'customer'


class CanBidOnTask(permissions.BasePermission):
    """
    Permission to check if user can bid on a task.
    """
    
    message = 'You cannot bid on this task.'
    
    def has_object_permission(self, request, view, obj):
        """Check if user can bid."""
        # Cannot bid on own task
        if obj.owner == request.user:
            return False
        
        # Task must be open
        if obj.status != 'open':
            return False
        
        # Bidding must be allowed
        if not obj.allow_bids:
            return False
        
        # User must be a tasker
        if request.user.role != 'tasker':
            return False
        
        return True
