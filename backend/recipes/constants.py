"""Модуль с константами приложения рецептов в проекте Foodgram."""


# Общие константы.
EMPTY_VALUE_DISPLAY = 'нет данных'

# Константы пользователей.
# Константы пользователя.
DEFAULT_USERNAME_FIELD = 'email'
DEFAULT_REQUIRED_FIELDS = ('username', 'first_name', 'last_name')
USERNAME_REG_EX = r'^[\w.@+-]+\Z'

# Константы пагинации.
DEFAULT_RECIPES_LIMIT_PARAM = 'recipes_limit'
DEFAULT_RECIPES_LIMIT_VALUE = 999

# Константы рецептов.
# Константы валидации.
MIN_COOKING_TIME = 1
MIN_AMOUNT = 1

# Константы пагинации.
DEFAULT_PAGE_SIZE = 6
DEFAULT_PAGE_LIMIT_PARAM = 'limit'
