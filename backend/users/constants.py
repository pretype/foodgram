"""Модуль с константами приложения пользователи проекта Foodgram."""

# Общие константы.
EMPTY_VALUE_DISPLAY = 'нет данных'

# Константы пользователей.
DEFAULT_USERNAME_FIELD = 'email'
DEFAULT_REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

# Константы пользовательских ролей.
USER = 'user'
ADMIN = 'admin'

# Константы валидации пользователей.
INVALID_USERNAMES = ('me',)

# Константы пагинации.
DEFAULT_RECIPES_LIMIT_PARAM = 'recipes_limit'
DEFAULT_RECIPES_LIMIT_VALUE = 999
