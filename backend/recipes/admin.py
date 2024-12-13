"""Модуль админ-зоны приложения рецептов в проекте Foodgram."""

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe

from .constants import EMPTY_VALUE_DISPLAY
from .models import (
    Favorite, Ingredient, IngredientRecipe,
    Recipe, ShoppingCart, Subscription, Tag
)

User = get_user_model()


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Админка пользователя."""

    list_display = (
        'id',
        'username',
        'full_name',
        'email',
        'thumbnail',
        'recipes_count',
        'authors_count',
        'followers_count'
    )
    search_fields = ('username', 'email')
    empty_value_display = EMPTY_VALUE_DISPLAY

    @admin.display(description='ФИО')
    def full_name(self, user):
        """Отдаёт имя и фамилию пользователя."""
        return f'{user.first_name} {user.last_name}'

    @admin.display(description='Число рецептов')
    def recipes_count(self, user):
        """Отдает число рецептов пользователя."""
        return user.recipes.count()

    @admin.display(description='Число подписок')
    def authors_count(self, user):
        """Отдает число подписок пользователя."""
        return user.authors.count()

    @admin.display(description='Число подписчиков')
    def followers_count(self, user):
        """Отдает число подписчиков пользователя."""
        return user.followers.count()

    @admin.display(description='Аватар')
    @mark_safe
    def thumbnail(self, user):
        """Отдаёт миниатюрный аватар пользователя."""
        if not user.avatar:
            return EMPTY_VALUE_DISPLAY
        return (
            '<img src="{}" width="75" height="75" />'.format(
                user.avatar.url
            )
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

    list_display = ('id', 'name', 'slug', 'recipe_count')
    search_fields = ('name', 'slug')
    empty_value_display = EMPTY_VALUE_DISPLAY

    @admin.display(description='Число рецептов')
    def recipe_count(self, tag):
        """Отдает число рецептов с продуктом."""
        return tag.recipes.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админка продуктов."""

    list_display = (
        'id', 'name',
        'measurement_unit',
        'recipe_count'
    )
    list_filter = ('measurement_unit',)
    search_fields = ('name', 'measurement_unit')
    empty_value_display = EMPTY_VALUE_DISPLAY

    @admin.display(description='Число рецептов')
    def recipe_count(self, ingredient):
        """Отдает число рецептов с продуктом."""
        return ingredient.recipes.count()


@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    """Админка модели продукт-рецептов."""

    list_display = ('id', 'ingredient', 'recipe', 'amount')
    search_fields = ('ingredient', 'recipe')
    empty_value_display = EMPTY_VALUE_DISPLAY


class FavShopCartAdminMixin(admin.ModelAdmin):
    """Родительский класс админок избранного и корзины."""

    list_display = ('id', 'user', 'recipe')
    empty_value_display = EMPTY_VALUE_DISPLAY

    class Meta:
        abstract = True


@admin.register(Favorite)
class FavoriteAdmin(FavShopCartAdminMixin):
    """Админка избранных рецептов."""


@admin.register(ShoppingCart)
class ShoppingCartAdmin(FavShopCartAdminMixin):
    """Админка списков покупок."""


class IngredientRecipeInline(admin.TabularInline):
    """Определение встраиваемых продукт-рецептов."""

    model = IngredientRecipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админка рецептов."""

    list_display = (
        'id', 'author', 'name',
        'image', 'cooking_time',
        '_tags', '_ingredients',
        'fav_count'
    )
    inlines = (IngredientRecipeInline,)
    list_filter = ('tags',)
    search_fields = ('name', 'author')
    empty_value_display = EMPTY_VALUE_DISPLAY

    @admin.display(description='Теги')
    def _tags(self, recipe):
        """Отдает перечень тегов рецепта."""
        return ''.join([f'{tag}, ' for tag in recipe.tags.all()])

    @admin.display(description='Продукты')
    def _ingredients(self, recipe):
        """Отдает перечень продуктов рецепта."""
        return ''.join([f'{ing}, ' for ing in recipe.ingredients.all()])

    @admin.display(description='Добавлений в избранное')
    def fav_count(self, recipe):
        """Отдаёт кол-во добавлений в избранное для рецепта."""
        return recipe.favorites.count()


admin.site.unregister(Group)
