"""Модуль с моделями приложения пользователи проекта Foodgram."""

from django.contrib.auth.models import AbstractUser
from django.db import models

from .constants import (ADMIN, DEFAULT_REQUIRED_FIELDS, DEFAULT_USERNAME_FIELD,
                        USER)


class User(AbstractUser):
    """Модель пользователя."""

    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Эл. почта'
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Пользователь'
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя пользователя'
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия пользователя'
    )
    avatar = models.ImageField(
        upload_to='users/avatars/',
        null=True,
        default=None,
        verbose_name='Аватар пользователя'
    )
    ROLE_CHOICES = [
        (USER, 'пользователь'),
        (ADMIN, 'админ')
    ]
    role = models.CharField(
        max_length=256,
        choices=ROLE_CHOICES,
        default=USER,
        verbose_name='Роль пользователя'
    )

    USERNAME_FIELD = DEFAULT_USERNAME_FIELD
    REQUIRED_FIELDS = DEFAULT_REQUIRED_FIELDS

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        """Проверка на админа."""
        return self.role == ADMIN or self.is_staff

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Модель подписки."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followed',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='following_followed'
            ),
        )

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
