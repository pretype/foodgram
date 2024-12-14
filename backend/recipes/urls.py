"""Модуль с маршрутизацией приложения рецептов проекта Foodgram."""

from django.urls import path

from .views import recipe_short_link

app_name = 'recipes'

urlpatterns = [
    path(
        '<int:recipe_id>/',
        recipe_short_link,
        name='recipe_short_link'
    )
]
