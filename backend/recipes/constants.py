"""Модуль с константами приложения рецептов в проекте Foodgram."""


# Общие константы.
EMPTY_VALUE_DISPLAY = 'нет данных'

# Константы пользователей.
# Константы пользователя.
DEFAULT_USERNAME_FIELD = 'email'
DEFAULT_REQUIRED_FIELDS = ('username', 'first_name', 'last_name')
USERNAME_REG_EX = r'^[\w.@+-]+\Z'

# Константы рецептов.
# Константы валидации.
MIN_COOKING_TIME = 1
MIN_AMOUNT = 1
