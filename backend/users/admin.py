"""Модуль админ-зоны приложения пользователи проекта Foodgram."""

from django.contrib import admin

from .constants import EMPTY_VALUE_DISPLAY
from .models import Subscription, User


class UserAdmin(admin.ModelAdmin):
    """Админка пользователя."""

    list_display = (
        'id',
        'email',
        'username',
        'first_name',
        'last_name'
    )
    search_fields = ('username', 'email')
    empty_value_display = EMPTY_VALUE_DISPLAY


class SubsriptionAdmin(admin.ModelAdmin):
    """Админка подписок."""

    list_display = (
        'id',
        'user',
        'author'
    )
    search_fields = ('user', 'author')
    empty_value_display = EMPTY_VALUE_DISPLAY


admin.site.register(User, UserAdmin)
admin.site.register(Subscription, SubsriptionAdmin)
