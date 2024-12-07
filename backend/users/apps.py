"""Модуль с настройками приложения пользователи проекта Foodgram."""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Настройки приложения пользователи."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = 'Пользователи'
