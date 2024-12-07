"""Модуль с валидаторами приложения рецептов проекта Foodgram."""

from django.core.exceptions import ValidationError

from .constants import MIN_AMOUNT, MIN_COOKING_TIME


def ingredients_or_tags_validation(ingredients_or_tags):
    """Валидатор ингредиентов и тегов."""
    if not ingredients_or_tags:
        raise ValidationError(
            'Добавление рецепта без ингредиентов или тегов недопустимо!'
        )

    ingredients_or_tags_list = [ing_or_tg for ing_or_tg in ingredients_or_tags]
    unique_ingredients_or_tags_list = set(ingredients_or_tags_list)

    if len(ingredients_or_tags_list) != len(unique_ingredients_or_tags_list):
        raise ValidationError(
            'Неуникальные ингредиенты или теги недопустимы!'
        )


def cooking_time_validation(cooking_time):
    """Валидатор времени готовки."""
    if cooking_time < MIN_COOKING_TIME:
        raise ValidationError(
            f'Минимальное время приготовления: {MIN_COOKING_TIME} минут!'
        )


def amounts_validation(amounts):
    """Валидатор минимального кол-ва ингредиента."""
    for amount in amounts:
        if amount < MIN_AMOUNT:
            raise ValidationError(
                f'Минимальный объём ингредиента в рецепте: {MIN_AMOUNT}!'
            )
