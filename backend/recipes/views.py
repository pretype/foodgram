"""Модуль с представлениями приложения рецептов проекта Foodgram."""

from django.http.response import Http404
from django.shortcuts import redirect
from django.views.decorators.http import require_GET

from .models import Recipe


@require_GET
def recipe_short_link(request, recipe_id_link):
    """Редирект на рецепт по короткой ссылке."""
    if not Recipe.objects.filter(id=recipe_id_link).exists():
        raise Http404('Такого рецепта нет!')
    return redirect(f'/recipes/{recipe_id_link}/')
