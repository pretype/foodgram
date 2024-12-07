# -*- coding: UTF-8 -*-
"""Модуль с представлениями приложения пользователи проекта Foodgram."""

from api.serializers import (SubscriptionsSerializer, UserCreateSerializer,
                             UserSerializer)
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import SetPasswordSerializer
from recipes.pagination import StandardResultsSetPagination
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .constants import DEFAULT_RECIPES_LIMIT_PARAM, DEFAULT_RECIPES_LIMIT_VALUE
from .models import Subscription

User = get_user_model()


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """Представление пользователя."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = StandardResultsSetPagination
    lookup_url_kwarg = 'user_id'

    def get_serializer_class(self):
        """Выбирает сериализатор для чтения или записи пользователя."""
        if self.request.method in permissions.SAFE_METHODS:
            return UserSerializer
        return UserCreateSerializer

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def me(self, request):
        """Отдает страницу текущего пользователя."""
        serializer_class = UserSerializer(
            request.user,
            context={'request': request}
        )
        return Response(
            serializer_class.data,
            status=status.HTTP_200_OK
        )

    @action(
        detail=False,
        methods=['put', 'delete'],
        permission_classes=(permissions.IsAuthenticated,),
        url_path='me/avatar'
    )
    def avatar(self, request):
        """Меняет или удаляет аватар пользователя."""
        serializer_class = UserSerializer(
            request.user,
            data=request.data,
            context={'request': request},
            partial=True
        )
        avatar = request.user.avatar

        if request.method == 'PUT':
            serializer_class.is_valid(raise_exception=True)
            serializer_class.save()
            return Response(
                {'avatar': serializer_class.data.get('avatar')},
                status=status.HTTP_200_OK
            )

        if request.method == 'DELETE':
            if avatar:
                avatar.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                'У пользователя нет своего аватара!',
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False,
        methods=['post'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def set_password(self, request, *args, **kwargs):
        """Изменяет пароль пользователя."""
        serializer_class = SetPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer_class.is_valid(raise_exception=True)
        request.user.set_password(
            serializer_class.data['new_password']
        )
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscriptions(self, request, *args, **kwargs):
        """Отдает подписки пользователя."""
        subscriptions = User.objects.filter(
            followed__user=self.request.user
        )
        page = self.paginate_queryset(subscriptions)
        serializer_class = SubscriptionsSerializer(
            page,
            many=True,
            context={
                'request': request,
                DEFAULT_RECIPES_LIMIT_PARAM: int(
                    request.GET.get(DEFAULT_RECIPES_LIMIT_PARAM,
                                    DEFAULT_RECIPES_LIMIT_VALUE)
                )
            }
        )
        return self.get_paginated_response(serializer_class.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscribe(self, request, *args, **kwargs):
        """Добавляет или убирает подписки пользователя."""
        author = get_object_or_404(User, id=kwargs['user_id'])
        user = request.user

        if request.method == 'POST':
            if author == user:
                return Response(
                    'Подписка на самого себя недопустима!',
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Subscription.objects.filter(
                user=user,
                author=author
            ).exists():
                return Response(
                    f'Подписка на пользователя "{author}" '
                    'уже оформлена!',
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer_class = SubscriptionsSerializer(
                author,
                data=request.data,
                context={
                    'request': request,
                    DEFAULT_RECIPES_LIMIT_PARAM: int(
                        request.GET.get(DEFAULT_RECIPES_LIMIT_PARAM,
                                        DEFAULT_RECIPES_LIMIT_VALUE)
                    )
                }
            )
            serializer_class.is_valid(raise_exception=True)
            Subscription.objects.create(user=user, author=author)
            return Response(
                serializer_class.data,
                status=status.HTTP_201_CREATED
            )

        if request.method == 'DELETE':
            subscriptions = Subscription.objects.filter(
                user=user,
                author=author
            )
            if subscriptions.exists():
                subscriptions.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                'Подписки не существует!',
                status=status.HTTP_400_BAD_REQUEST
            )
