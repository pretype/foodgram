"""Модуль админ-зоны приложения рецептов в проекте Foodgram."""

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe

from .constants import EMPTY_VALUE_DISPLAY
from .models import (
    Favorite, Ingredient, Recipe,
    RecipeIngredient, ShoppingCart, Subscription, Tag
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

    @admin.display(description='Рецептов')
    def recipes_count(self, user):
        """Отдает число рецептов пользователя."""
        return user.recipes.count()

    @admin.display(description='Подписок')
    def authors_count(self, user):
        """Отдает число подписок пользователя."""
        return user.followers.count()

    @admin.display(description='Подписчиков')
    def followers_count(self, user):
        """Отдает число подписчиков пользователя."""
        return user.authors.count()

    @admin.display(description='Аватар')
    @mark_safe
    def thumbnail(self, user):
        """Отдаёт миниатюрный аватар пользователя."""
        return (
            f'<img src="{user.avatar.url}" width="75" height="75" />'
            if user.avatar else ''
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

    @admin.display(description='Рецептов')
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

    @admin.display(description='Рецептов')
    def recipe_count(self, ingredient):
        """Отдает число рецептов с продуктом."""
        return ingredient.recipes.count()


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Админка модели продуктов в рецепте."""

    list_display = (
        'id', 'ingredient',
        'recipe', '_measurement_unit',
        'amount'
    )
    search_fields = ('ingredient', 'recipe')
    empty_value_display = EMPTY_VALUE_DISPLAY

    @admin.display(description='Ед.изм')
    def _measurement_unit(self, recipe_ingredient):
        """Отдаёт единицу измерения продукта."""
        return recipe_ingredient.ingredient.measurement_unit


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


class RecipeIngredientInline(admin.TabularInline):
    """Определение встраиваемых продуктов в рецепте."""

    model = RecipeIngredient
    readonly_fields = ('_measurement_unit',)

    @admin.display(description='Ед.изм')
    def _measurement_unit(self, recipe_ingredient):
        """Отдаёт единицу измерения продукта."""
        return recipe_ingredient.ingredient.measurement_unit


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админка рецептов."""

    list_display = (
        'id', 'author', 'name',
        'thumbnail', 'cooking_time',
        '_tags', '_ingredients',
        'fav_count'
    )
    inlines = (RecipeIngredientInline,)
    list_filter = ('tags', 'author')
    search_fields = ('name', 'author')
    empty_value_display = EMPTY_VALUE_DISPLAY

    @admin.display(description='Теги')
    @mark_safe
    def _tags(self, recipe):
        """Отдает перечень тегов рецепта."""
        return '<br>'.join(
            f'{tag}' for tag in recipe.tags.all()
        )

    @admin.display(description='Продукты')
    @mark_safe
    def _ingredients(self, recipe):
        """Отдает перечень продуктов рецепта."""
        return '<br>'.join(
            '{} ({}) — {}'.format(
                rec_ing.ingredient.name,
                rec_ing.ingredient.measurement_unit,
                rec_ing.amount
            ) for rec_ing in recipe.recipe_ingredients.all()
        )

    @admin.display(description='Изображение')
    @mark_safe
    def thumbnail(self, recipe):
        """Отдаёт миниатюрное изображение рецепта."""
        return (
            f'<img src="{recipe.image.url}" width="75" height="75" />'
            if recipe.image else ''
        )

    @admin.display(description='В избранном')
    def fav_count(self, recipe):
        """Отдаёт кол-во добавлений в избранное для рецепта."""
        return recipe.favorites.count()


admin.site.unregister(Group)
