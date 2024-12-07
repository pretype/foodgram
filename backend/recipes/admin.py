"""Модуль админ-зоны приложения рецептов в проекте Foodgram."""

from django.contrib import admin
from django.db.models import Count

from .constants import EMPTY_VALUE_DISPLAY, FIRST_IN_LIST
from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Tag, TagRecipe)


class TagAdmin(admin.ModelAdmin):
    """Админка тегов."""

    list_display = ('id', 'name', 'slug')
    list_filter = ('name',)
    search_fields = ('name',)
    empty_value_display = EMPTY_VALUE_DISPLAY


class IngredientAdmin(admin.ModelAdmin):
    """Админка ингредиентов."""

    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    empty_value_display = EMPTY_VALUE_DISPLAY


class IngredientRecipeAdmin(admin.ModelAdmin):
    """Админка модели ингредиент-рецептов."""

    list_display = ('id', 'ingredient', 'recipe', 'amount')
    search_fields = ('ingredient', 'recipe')
    empty_value_display = EMPTY_VALUE_DISPLAY


class TagRecipeAdmin(admin.ModelAdmin):
    """Админка модели тег-рецептов."""

    list_display = ('id', 'tag', 'recipe')
    list_filter = ('tag',)
    search_fields = ('tag', 'recipe')
    empty_value_display = EMPTY_VALUE_DISPLAY


class FavoriteAdmin(admin.ModelAdmin):
    """Админка избранных рецептов."""

    list_display = ('id', 'user', 'recipe')
    list_filter = ('user',)
    empty_value_display = EMPTY_VALUE_DISPLAY


class ShoppingCartAdmin(admin.ModelAdmin):
    """Админка списков покупок."""

    list_display = ('id', 'user', 'recipe')
    list_filter = ('user',)
    empty_value_display = EMPTY_VALUE_DISPLAY


class IngredientRecipeInline(admin.TabularInline):
    """Определение встраиваемых ингредиент-рецептов."""

    model = IngredientRecipe


class TagRecipeAdminInline(admin.TabularInline):
    """Определение встраиваемых тег-рецептов."""

    model = TagRecipe


class RecipeAdmin(admin.ModelAdmin):
    """Админка рецептов."""

    list_display = (
        'id', 'author', 'name',
        'image', 'text', 'fav_count'
    )
    inlines = (IngredientRecipeInline, TagRecipeAdminInline)
    list_filter = ('tags',)
    search_fields = ('name', 'author')
    empty_value_display = EMPTY_VALUE_DISPLAY

    @admin.display(description='Добавлений в избранное')
    def fav_count(self, obj):
        """Отдаёт кол-во добавлений в избранное для рецепта."""
        count = Favorite.objects.filter(
            recipe=obj
        ).values('recipe').annotate(
            count=Count('user')
        ).values('count')

        if count:
            return count[FIRST_IN_LIST]['count']
        return 0


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(IngredientRecipe, IngredientRecipeAdmin)
admin.site.register(TagRecipe, TagRecipeAdmin)
