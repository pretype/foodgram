"""Модуль с утилитами приложения API проекта Foodgram."""

from datetime import datetime


def shopping_cart_content(ingredients_and_amounts, recipes, user):
    """Формирование содержания файла со списком покупок."""
    current_date = datetime.now().strftime('%d.%m.%y')
    number_of_item = 0
    ingredients_and_amounts_list = []

    for ingredient_and_amount in ingredients_and_amounts:
        number_of_item += 1
        ingredients_and_amounts_list.append(
            f'{number_of_item}. '
            f'{ingredient_and_amount[0].capitalize()} '
            f'({ingredient_and_amount[1]}) — '
            f'{ingredient_and_amount[2]}'
        )

    number_of_item = 0
    recipes_list = []

    for recipe in recipes:
        number_of_item += 1
        recipes_list.append(
            f'{number_of_item}. '
            f'{recipe[0]}.'
        )

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
