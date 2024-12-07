"""Модуль с настройками приложения рецепты проекта Foodgram."""

from django.apps import AppConfig


class RecipesConfig(AppConfig):
    """Настройки приложения рецепты."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recipes'
    verbose_name = 'Рецепты'
