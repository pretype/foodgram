"""Модуль с настройками прав пользователей проекта Foodgram."""

from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Пользовательское разрешение.

    Автору объекта разрешены просмотр и изменение объекта.
    Другим пользователям разрешен только просмотр объекта.
    """

    def has_object_permission(self, request, view, recipe):
        return (
            request.method in permissions.SAFE_METHODS
            or recipe.author == request.user
        )
