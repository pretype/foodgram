"""Модуль с настройками приложения API проекта Foodgram."""

from django.apps import AppConfig


class ApiConfig(AppConfig):
    """Настройки приложения API."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    verbose_name = 'API'
