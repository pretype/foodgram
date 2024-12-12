# -*- coding: UTF-8 -*-
"""Модуль с представлениями приложения API проекта Foodgram."""

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_GET
from djoser.serializers import SetPasswordSerializer, UserCreateSerializer
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.serializers import ValidationError

from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Subscription, Tag)
from .filters import IngredientFilter, RecipeFilter
from .pagination import StandardResultsSetPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (IngredientSerializer, RecipeModificateSerializer,
                          RecipePresentitiveSerializer, RecipeSerializer,
                          SubscriptionsSerializer, TagSerializer,
                          UserSerializer)
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
        elif self.action == 'set_password':
            return SetPasswordSerializer
        return UserCreateSerializer

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
            if not avatar:
                raise ValidationError(
                    'У пользователя нет своего аватара!'
                )
            avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscriptions(self, request, *args, **kwargs):
        """Отдает подписки пользователя."""
        subscriptions = User.objects.filter(
            authors__user=self.request.user
        )
        page = self.paginate_queryset(subscriptions)
        serializer_class = SubscriptionsSerializer(
            page,
            many=True,
            context={'request': request}
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
                raise ValidationError(
                    'Подписка на самого себя недопустима!'
                )
            sub, created = Subscription.objects.get_or_create(
                user=user,
                author=author
            )
            if not created:
                raise ValidationError(
                    f'Подписка на пользователя "{author}" '
                    'уже оформлена!'
                )
            serializer_class = SubscriptionsSerializer(
                author,
                context={'request': request}
            )
            return Response(
                serializer_class.data,
                status=status.HTTP_201_CREATED
            )

        if request.method == 'DELETE':
            get_object_or_404(
                Subscription,
                user=user,
                author=author
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


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


@require_GET
def short_link(requset, recipe_id_link):
    """Редирект на рецепт по короткой ссылке."""
    get_object_or_404(Recipe, id=recipe_id_link)
    return redirect(f'/recipes/{recipe_id_link}/')


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

    def recipes_add_to_delete_from_method(self, model):
        """Метод добавления и удаления рецепта в других моделях."""
        recipe = get_object_or_404(Recipe, id=self.kwargs['recipe_id'])
        user = self.request.user

        if self.request.method == 'POST':
            rec_in, created = model.objects.get_or_create(
                user=user,
                recipe=recipe
            )
            if not created:
                raise ValidationError(
                    'Рецепт уже добавлен!'
                )
            serializer_class = RecipePresentitiveSerializer(
                recipe,
                context={'request': self.request}
            )
            return Response(
                serializer_class.data,
                status=status.HTTP_201_CREATED
            )

        if self.request.method == 'DELETE':
            get_object_or_404(model, user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def favorite(self, request, *args, **kwargs):
        """Добавляет или убирает рецепт в избранных рецептах."""
        return self.recipes_add_to_delete_from_method(Favorite)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def shopping_cart(self, request, *args, **kwargs):
        """Добавляет или убирает рецепт в списке покупок."""
        return self.recipes_add_to_delete_from_method(ShoppingCart)

    @action(
        detail=True,
        methods=['get'],
        permission_classes=(permissions.AllowAny,),
        url_path='get-link'
    )
    def get_link(self, request, *args, **kwargs):
        """Отдаёт короткую ссылку на текущий рецепт."""
        recipe = get_object_or_404(Recipe, id=kwargs['recipe_id'])
        recipe_link = reverse('short_link', args=(recipe.id,))
        return Response(
            {
                'short-link': request.build_absolute_uri(
                    recipe_link
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
            IngredientRecipe.objects.filter(
                recipe__shoppingcarts__user=user
            ).values(
                'ingredient'
            ).annotate(
                summarized_amount=Sum('amount')
            ).values_list(
                'ingredient__name',
                'ingredient__measurement_unit',
                'summarized_amount'
            )
        )
        recipes = ShoppingCart.objects.filter(
            user=user
        ).values('recipe').values_list('recipe__name',)

        return FileResponse(
            shopping_cart_content(
                ingredients_and_amounts,
                recipes,
                user
            ),
            content_type='text/plain; utf-8'
        )
