"""Модуль с утилитами приложения API проекта Foodgram."""

from datetime import datetime


def shopping_cart_content(ingredients_and_amounts, recipes, user):
    """Формирование содержания файла со списком покупок."""
    current_date = datetime.now().strftime('%d.%m.%y')
    ingredients_and_amounts_list = [
        '{}. {} ({}) — {}'.format(
            number_of_item,
            ingredient.capitalize(),
            measurement_unit,
            amount,
        )
        for number_of_item, (
            ingredient, measurement_unit, amount
        ) in enumerate(ingredients_and_amounts, start=1)
    ]

    recipes_list = [
        '{}. {}'.format(
            number_of_item,
            recipe
        )
        for number_of_item, recipe in enumerate(
            recipes, start=1
        )
    ]

    return '\n'.join(
        [
            'Список покупок пользователя: '
            f'"{user.first_name} {user.last_name}"',
            f'Дата: {current_date}',
            'Список необходимых продуктов:',
            *ingredients_and_amounts_list,
            'Список рецептов:',
            *recipes_list
        ]
    )
