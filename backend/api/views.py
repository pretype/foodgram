# -*- coding: UTF-8 -*-
"""Модуль с представлениями приложения API проекта Foodgram."""

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.serializers import ValidationError

from recipes.models import (
    Favorite, Ingredient,
    Recipe, RecipeIngredient,
    ShoppingCart, Subscription, Tag
)
from .filters import IngredientFilter, RecipeFilter
from .pagination import StandardResultsSetPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    IngredientSerializer, RecipeModificateSerializer,
    RecipeSerializer, RecipeShortSerializer,
    SubscriptionsSerializer, TagSerializer,
    UserSerializer
)
from .utils import shopping_cart_content

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    """Представление пользователя."""

    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    pagination_class = StandardResultsSetPagination
    lookup_url_kwarg = 'user_id'

    def get_serializer_class(self):
        """Выбирает подходящий сериализатор."""
        if self.request.method in permissions.SAFE_METHODS:
            return UserSerializer
        return super().get_serializer_class()

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def me(self, request):
        """Отдает страницу текущего пользователя."""
        return super().me(request)

    @action(
        detail=False,
        methods=['put', 'delete'],
        permission_classes=(permissions.IsAuthenticated,),
        url_path='me/avatar'
    )
    def avatar(self, request):
        """Меняет или удаляет аватар пользователя."""
        avatar = request.user.avatar

        if request.method == 'DELETE':
            if not avatar:
                raise ValidationError(
                    'У пользователя нет аватара!'
                )
            avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = UserSerializer(
            request.user,
            data=request.data,
            context={'request': request},
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'avatar': serializer.data.get('avatar')},
            status=status.HTTP_200_OK
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscriptions(self, request, *args, **kwargs):
        """Отдает подписки пользователя."""
        return self.get_paginated_response(
            SubscriptionsSerializer(
                self.paginate_queryset(
                    User.objects.filter(
                        authors__user=self.request.user
                    )
                ),
                many=True,
                context={'request': request}
            ).data
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscribe(self, request, *args, **kwargs):
        """Добавляет или убирает подписки пользователя."""
        author = get_object_or_404(User, id=kwargs['user_id'])
        user = request.user

        if request.method == 'DELETE':
            get_object_or_404(
                Subscription,
                user=user,
                author=author
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        if author == user:
            raise ValidationError(
                'Подписка на самого себя недопустима!'
            )
        _, created = Subscription.objects.get_or_create(
            user=user,
            author=author
        )
        if not created:
            raise ValidationError(
                f'Подписка на пользователя "{author}" '
                'уже оформлена!'
            )
        return Response(
            SubscriptionsSerializer(
                author,
                context={'request': request}
            ).data,
            status=status.HTTP_201_CREATED
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление продуктов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """Представление рецептов."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,
                          permissions.IsAuthenticatedOrReadOnly)
    pagination_class = StandardResultsSetPagination
    lookup_url_kwarg = 'recipe_id'
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Выбирает сериализатор чтения или записи рецепта."""
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeSerializer
        return RecipeModificateSerializer

    def recipes_add_to_delete_from(self, model):
        """Метод добавления и удаления рецепта в других моделях."""
        recipe = get_object_or_404(Recipe, id=self.kwargs['recipe_id'])
        user = self.request.user

        if self.request.method == 'DELETE':
            get_object_or_404(model, user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        _, created = model.objects.get_or_create(
            user=user,
            recipe=recipe
        )
        if not created:
            raise ValidationError(
                'Рецепт уже добавлен!'
            )
        return Response(
            RecipeShortSerializer(
                recipe,
                context={'request': self.request}
            ).data,
            status=status.HTTP_201_CREATED
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def favorite(self, request, *args, **kwargs):
        """Добавляет или убирает рецепт в избранных рецептах."""
        return self.recipes_add_to_delete_from(Favorite)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def shopping_cart(self, request, *args, **kwargs):
        """Добавляет или убирает рецепт в списке покупок."""
        return self.recipes_add_to_delete_from(ShoppingCart)

    @action(
        detail=True,
        methods=['get'],
        permission_classes=(permissions.AllowAny,),
        url_path='get-link'
    )
    def get_link(self, request, *args, **kwargs):
        """Отдаёт короткую ссылку на текущий рецепт."""
        recipe_id = kwargs['recipe_id']
        if not Recipe.objects.filter(id=recipe_id).exists():
            raise ValidationError(
                f'Рецепта с id "{recipe_id}" не существует!'
            )
        return Response(
            {
                'short-link': request.build_absolute_uri(
                    reverse(
                        'recipes:recipe_short_link',
                        args=(recipe_id,)
                    )
                )
            },
            status=status.HTTP_200_OK
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Преобразует данные списка покупок и выгружает их в .txt."""
        user = request.user
        if not user.shoppingcarts.exists():
            raise ValidationError(
                'Список покупок пуст!'
            )
        ingredients_and_amounts = (
            RecipeIngredient.objects.filter(
                recipe__shoppingcarts__user=user
            ).values(
                'ingredient'
            ).annotate(
                summarized_amount=Sum('amount')
            ).order_by(
                'ingredient__name',
            ).values_list(
                'ingredient__name',
                'ingredient__measurement_unit',
                'summarized_amount'
            )
        )

        recipes = Recipe.objects.filter(
            shoppingcarts__user=user
        ).all().order_by('name',)

        return FileResponse(
            shopping_cart_content(
                ingredients_and_amounts,
                recipes,
                user
            ),
            content_type='text/plain; utf-8'
        )
