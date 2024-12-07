# -*- coding: UTF-8 -*-
"""Модуль с представлениями приложения рецептов проекта Foodgram."""

import io

from api.serializers import (FavoriteSerializer, IngredientSerializer,
                             RecipeAddSerializer, RecipeSerializer,
                             ShoppingCartSerializer, TagSerializer)
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from reportlab.pdfbase import pdfmetrics, ttfonts
from reportlab.pdfgen import canvas
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from users.permissions import IsAdminOrAuthorOrReadOnly, IsAdminOrReadOnly

from .constants import (FIRST_IN_LIST, FONT_SIZE, ITEMS_PER_PAGE,
                        MAX_PAGES_COUNT, SECOND_IN_LIST, THIRD_IN_LIST, X_AXIS,
                        Y_AXIS, Y_AXIS_SHIFT)
from .filters import IngredientFilter, RecipeFilter
from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Tag)
from .pagination import StandardResultsSetPagination

User = get_user_model()


class ListRetrieveGenericMixin(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """Общие для тегов, ингредиентов и рецептов миксины."""


class TagViewSet(ListRetrieveGenericMixin):
    """Представление тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None


class IngredientViewSet(ListRetrieveGenericMixin):
    """Представление ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None
    filterset_class = IngredientFilter


class RecipeViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    ListRetrieveGenericMixin
):
    """Представление рецептов."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAdminOrAuthorOrReadOnly,)
    pagination_class = StandardResultsSetPagination
    lookup_url_kwarg = 'recipe_id'
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Выбирает сериализатор чтения или записи рецепта."""
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeSerializer
        return RecipeAddSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def favorite(self, request, *args, **kwargs):
        """Добавляет или убирает рецепт в избранных рецептах."""
        recipe = get_object_or_404(Recipe, id=kwargs['recipe_id'])
        user = request.user

        if request.method == 'POST':
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    'Рецепт уже в избранном!',
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer_class = FavoriteSerializer(
                data=request.data,
                context={'request': request}
            )
            serializer_class.is_valid(raise_exception=True)
            serializer_class.save(user=user, recipe=recipe)
            return Response(
                serializer_class.data,
                status=status.HTTP_201_CREATED
            )

        if request.method == 'DELETE':
            favorite_recipes = Favorite.objects.filter(
                user=user,
                recipe=recipe
            )
            if favorite_recipes.exists():
                favorite_recipes.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                'Рецепта нет в избранном!',
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def shopping_cart(self, request, *args, **kwargs):
        """Добавляет или убирает рецепт в списке покупок."""
        recipe = get_object_or_404(Recipe, id=kwargs['recipe_id'])
        user = request.user

        if request.method == 'POST':
            if ShoppingCart.objects.filter(
                user=user, recipe=recipe
            ).exists():
                return Response(
                    'Рецепт уже в списке покупок!',
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer_class = ShoppingCartSerializer(
                data=request.data,
                context={'request': request}
            )
            serializer_class.is_valid(raise_exception=True)
            serializer_class.save(user=user, recipe=recipe)
            return Response(
                serializer_class.data,
                status=status.HTTP_201_CREATED
            )

        if request.method == 'DELETE':
            shopping_cart_recipes = ShoppingCart.objects.filter(
                user=user,
                recipe=recipe
            )
            if shopping_cart_recipes.exists():
                shopping_cart_recipes.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                'Рецепта нет в списке покупок!',
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=True,
        methods=['get'],
        permission_classes=(permissions.AllowAny,),
        url_path='get-link'
    )
    def get_link(self, request, *args, **kwargs):
        """Отдаёт ссылку на текущий рецепт."""
        return Response(
            {
                'short-link': request.build_absolute_uri(
                    f'/recipes/{kwargs["recipe_id"]}/'
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
        """Преобразует данные списка покупок и выгружает их в pdf."""
        user = request.user
        if user.shopping_cart.exists():
            ingredients_and_amounts = (
                IngredientRecipe.objects.filter(
                    recipe__shopping_cart__user=user
                ).values(
                    'ingredient'
                ).annotate(
                    summarized_amount=Sum('amount')
                ).values_list(
                    'ingredient__name',
                    'summarized_amount',
                    'ingredient__measurement_unit'
                )
            )
            custom_font = ttfonts.TTFont(
                'DejaVuSans', 'DejaVuSans.ttf'
            )
            pdfmetrics.registerFont(custom_font)
            buff = io.BytesIO()
            pdf_object = canvas.Canvas(buff, bottomup=False)
            ingredients_and_amounts = list(ingredients_and_amounts)
            number_of_pages = 0
            number_of_item = 0
            number_of_items_per_page = 0
            x_axis = X_AXIS
            while number_of_pages < MAX_PAGES_COUNT:
                pdf_object.setFont('DejaVuSans', FONT_SIZE)
                y_axis = Y_AXIS
                pdf_object.drawString(
                    x_axis,
                    y_axis,
                    'Список покупок пользователя: '
                    f'"{user.first_name} {user.last_name}".'
                )
                y_axis += Y_AXIS_SHIFT
                pdf_object.drawString(
                    x_axis,
                    y_axis,
                    '№п/п. Ингредиент (Ед. измерения) — Кол-во')
                number_of_items_per_page = 0
                number_of_pages += 1
                while len(ingredients_and_amounts):
                    if number_of_items_per_page <= ITEMS_PER_PAGE:
                        number_of_item += 1
                        y_axis += Y_AXIS_SHIFT
                        ingredient = ingredients_and_amounts.pop()
                        pdf_object.drawString(
                            x_axis,
                            y_axis,
                            f'{number_of_item}. '
                            f'{ingredient[FIRST_IN_LIST]} '
                            f'({ingredient[THIRD_IN_LIST]}) — '
                            f'{ingredient[SECOND_IN_LIST]}')
                        number_of_items_per_page += 1
                        continue
                    break
                pdf_object.showPage()
                if ingredients_and_amounts:
                    continue
                break
            pdf_object.save()
            buff.seek(0)
            return FileResponse(
                buff,
                as_attachment=True,
                filename='shopping-list.pdf',
                status=status.HTTP_200_OK
            )
        return Response(
            'Список покупок пуст!',
            status=status.HTTP_400_BAD_REQUEST
        )
