"""Модуль с настройками прав пользователей проекта Foodgram."""

from rest_framework import permissions


class IsAdminOrAuthorOrReadOnly(permissions.BasePermission):
    """Определение прав админа и автора."""

    def has_permission(self, request, view):
        """Определение доступа."""
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        """Определение доступа к объекту."""
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or (
                request.user.is_authenticated
                and request.user.is_admin
            )
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """Определение прав админа и автора."""

    def has_object_permission(self, request, view, obj):
        """Определение доступа к объекту."""
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_admin
        )
