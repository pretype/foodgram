"""Модуль с фильтрами приложения рецептов проекта Foodgram."""

from django.contrib.auth import get_user_model
from django_filters.rest_framework import FilterSet, filters

from .models import Ingredient, Recipe, Tag

User = get_user_model()


class IngredientFilter(FilterSet):
    """Поиск по названию для ингредиентов."""

    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    """Набор фильтров для рецептов."""

    author = filters.ModelChoiceFilter(
        queryset=User.objects.all(),
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = filters.BooleanFilter(
        method='is_favorited_custom_filter'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='is_in_shopping_cart_custom_filter'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author')

    def is_favorited_custom_filter(self, queryset, name, value):
        """Фильтрует по избранности рецепта."""
        user = self.request.user
        if user.is_authenticated and value:
            return queryset.filter(favorites__user=user)
        return queryset

    def is_in_shopping_cart_custom_filter(self, queryset, name, value):
        """Фильтрует по включению рецепта в список покупок."""
        user = self.request.user
        if user.is_authenticated and value:
            return queryset.filter(shopping_cart__user=user)
        return queryset
