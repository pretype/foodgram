"""Модуль с валидаторами приложения пользователи проекта Foodgram."""

import re

from django.core.exceptions import ValidationError

from .constants import INVALID_USERNAMES


def username_validation(username):
    """Валидатор юзернейма пользователя."""
    if username in INVALID_USERNAMES:
        raise ValidationError(
            f'Имя пользователя "{username}" - недопустимо!'
        )
    matching_chars = re.findall(r'^[\w.@+-]+\Z', username)
    if username and not matching_chars:
        raise ValidationError(
            f'Имя пользователя "{username}" - содержит недопустимые символы!'
        )


def avatar_validation(avatar):
    """Валидатор аватара пользователя."""
    if avatar is None:
        raise ValidationError(
            'Пользовательский аватар не выбран!'
        )
