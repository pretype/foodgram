"""Модуль админ-зоны приложения рецептов в проекте Foodgram."""

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group
from django.db.models import Count
from django.utils.safestring import mark_safe

from .constants import EMPTY_VALUE_DISPLAY
from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Subscription, Tag)

User = get_user_model()


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Админка пользователя."""

    list_display = (
        'id',
        'username',
        'full_name',
        'email',
        'thumbnail'
    )
    search_fields = ('username', 'email')
    empty_value_display = EMPTY_VALUE_DISPLAY

    @admin.display(description='ФИО')
    def full_name(self, user):
        """Отдаёт имя и фамилию пользователя."""
        return f'{user.first_name} {user.last_name}'

    @admin.display(description='Аватар')
    @mark_safe
    def thumbnail(self, user):
        """Отдаёт миниатюрный аватар пользователя."""
        if user.avatar:
            return (
                '<img src="%s" width="75" height="75" />' % user.avatar.url
            )


@admin.register(Subscription)
class SubcsriptionAdmin(admin.ModelAdmin):
    """Админка подписок."""

    list_display = (
        'id',
        'user',
        'author'
    )
    search_fields = ('user', 'author')
    empty_value_display = EMPTY_VALUE_DISPLAY


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админка тегов."""

    list_display = ('id', 'name', 'slug')
    search_fields = ('name',)
    empty_value_display = EMPTY_VALUE_DISPLAY


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админка продуктов."""

    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    empty_value_display = EMPTY_VALUE_DISPLAY


@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    """Админка модели продукт-рецептов."""

    list_display = ('id', 'ingredient', 'recipe', 'amount')
    search_fields = ('ingredient', 'recipe')
    empty_value_display = EMPTY_VALUE_DISPLAY


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админка избранных рецептов."""

    list_display = ('id', 'user', 'recipe')
    empty_value_display = EMPTY_VALUE_DISPLAY


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Админка списков покупок."""

    list_display = ('id', 'user', 'recipe')
    empty_value_display = EMPTY_VALUE_DISPLAY


class IngredientRecipeInline(admin.TabularInline):
    """Определение встраиваемых продукт-рецептов."""

    model = IngredientRecipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админка рецептов."""

    list_display = (
        'id', 'author', 'name',
        'image', 'text', 'fav_count'
    )
    inlines = (IngredientRecipeInline,)
    list_filter = ('tags',)
    search_fields = ('name', 'author')
    empty_value_display = EMPTY_VALUE_DISPLAY

    @admin.display(description='Добавлений в избранное')
    def fav_count(self, recipe):
        """Отдаёт кол-во добавлений в избранное для рецепта."""
        count = Favorite.objects.filter(
            recipe=recipe
        ).values('recipe').annotate(
            count=Count('user')
        ).values_list('count',)

        if count:
            return count[0]
        return 0


admin.site.unregister(Group)
