"""Модуль с настройками прав пользователей проекта Foodgram."""

from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Определение прав автора."""

    def has_object_permission(self, request, view, recipe):
        """Определение доступа к объекту."""
        return (
            request.method in permissions.SAFE_METHODS
            or recipe.author == request.user
        )
