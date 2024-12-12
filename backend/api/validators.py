"""Модуль с валидаторами приложения рецептов проекта Foodgram."""


from django.core.exceptions import ValidationError


def ingredients_or_tags_validation(ingredients_or_tags):
    """Валидатор продуктов и тегов."""
    if not ingredients_or_tags:
        raise ValidationError(
            'Добавление рецепта без продуктов или тегов недопустимо!'
        )

    ingredients_or_tags_list = [ing_or_tg for ing_or_tg in ingredients_or_tags]
    unique_ingredients_or_tags_list = set(ingredients_or_tags_list)

    if len(ingredients_or_tags_list) != len(unique_ingredients_or_tags_list):
        raise ValidationError(
            'Неуникальные продукты или теги недопустимы!'
        )
