"""Модуль с сериализаторами проекта Foodgram."""

import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from recipes.validators import (amounts_validation, cooking_time_validation,
                                ingredients_or_tags_validation)
from rest_framework import serializers
from users.constants import (DEFAULT_RECIPES_LIMIT_PARAM,
                             DEFAULT_RECIPES_LIMIT_VALUE,
                             DEFAULT_REQUIRED_FIELDS, DEFAULT_USERNAME_FIELD)
from users.models import Subscription, User
from users.validators import avatar_validation, username_validation


class Base64ImageField(serializers.ImageField):
    """Сериализатор данных в Base64 кодировке."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class UserSerializer(UserSerializer):
    """Сериализатор пользователя."""

    is_subscribed = serializers.SerializerMethodField(
        read_only=True,
        method_name='get_is_subscribed'
    )
    avatar = Base64ImageField(allow_null=True)

    class Meta:
        model = User
        fields = (
            'id',
            DEFAULT_USERNAME_FIELD,
            *DEFAULT_REQUIRED_FIELDS,
            'is_subscribed',
            'avatar'
        )

    def validate(self, data):
        """Валидация аватара."""
        avatar_validation(data.get('avatar'))
        return data

    def get_is_subscribed(self, obj):
        """Проверяет подписку на пользователя."""
        current_user = self.context['request'].user
        return bool(
            current_user.is_authenticated
            and Subscription.objects.filter(
                user=current_user,
                author=obj
            ).exists()
        )


class UserCreateSerializer(UserCreateSerializer):
    """Сериализатор добавления пользователя."""

    class Meta:
        model = User
        fields = (
            'id',
            DEFAULT_USERNAME_FIELD,
            *DEFAULT_REQUIRED_FIELDS,
            'password'
        )

    def validate_username(self, obj):
        """Валидация имени пользователя."""
        username_validation(obj)
        return obj


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Сериализатор подписок."""

    is_subscribed = serializers.SerializerMethodField(
        read_only=True,
        method_name='get_is_subscribed'
    )
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            DEFAULT_USERNAME_FIELD,
            *DEFAULT_REQUIRED_FIELDS,
            'is_subscribed',
            'avatar',
            'recipes',
            'recipes_count'
        )
        extra_kwargs = {
            'email': {'required': False},
            'username': {'required': False},
            'first_name': {'required': False},
            'last_name': {'required': False}
        }

    def get_recipes_count(self, obj):
        """Отдает кол-во рецептов."""
        return obj.recipes.count()

    def get_is_subscribed(self, obj):
        """Проверяет подписку на пользователя."""
        current_user = self.context['request'].user
        return bool(
            current_user.is_authenticated
            and Subscription.objects.filter(
                user=current_user,
                author=obj
            ).exists()
        )

    def get_recipes(self, obj):
        """Отдаёт список рецептов с возможностью лимитирования."""
        request = self.context['request']
        return RecipePresentitiveSerializer(
            obj.recipes.all()[
                :self.context.get(
                    DEFAULT_RECIPES_LIMIT_PARAM,
                    DEFAULT_RECIPES_LIMIT_VALUE)
            ],
            context={'request': request},
            many=True
        ).data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор модели игредиент-рецепт."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта."""

    author = UserSerializer(read_only=True)
    tags = TagSerializer(
        read_only=True,
        many=True
    )
    ingredients = IngredientRecipeSerializer(
        read_only=True,
        many=True,
        source='ingredient_in_recipe'
    )
    image = Base64ImageField(allow_null=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'name',
            'text',
            'tags',
            'ingredients',
            'image',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def get_is_favorited(self, obj):
        """Проверяет избранность рецепта."""
        user = self.context['request'].user
        return (
            user.is_authenticated
            and Favorite.objects.filter(
                user=user,
                recipe=obj
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        """Проверяет включение рецепта в список покупок."""
        user = self.context['request'].user
        return (
            user.is_authenticated
            and ShoppingCart.objects.filter(
                user=user,
                recipe=obj
            ).exists()
        )


class IngredientAddRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор добавления ингредиента в рецепт."""

    id = serializers.PrimaryKeyRelatedField(
        required=True,
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'amount'
        )


class RecipeAddSerializer(serializers.ModelSerializer):
    """Сериализатор добавления рецепта."""

    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        required=True,
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = IngredientAddRecipeSerializer(
        required=True,
        many=True
    )
    image = Base64ImageField(allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def add_ingredients(self, ingredients, recipe):
        """Отдаёт или добавляет ингрединты в базу."""
        for _ingredient in ingredients:
            IngredientRecipe.objects.get_or_create(
                recipe=recipe,
                ingredient=_ingredient['id'],
                amount=_ingredient['amount']
            )

    def validate_tags(self, obj):
        """Валидация тегов рецепта."""
        ingredients_or_tags_validation(obj)
        return obj

    def validate_ingredients(self, obj):
        """Валидация ингредиентов рецепта."""
        ingredients = [ing['id'] for ing in obj]
        ingredients_or_tags_validation(ingredients)
        amounts = [ing['amount'] for ing in obj]
        amounts_validation(amounts)
        return obj

    def validate_cooking_time(self, obj):
        """Валидация времени готовки."""
        cooking_time_validation(obj)
        return obj

    def to_representation(self, instance):
        """Преобразовывает данные в подходящее представление."""
        return RecipeSerializer(
            instance,
            context=self.context
        ).data

    def create(self, validated_data):
        """Создание рецепта."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        self.add_ingredients(
            ingredients,
            recipe
        )
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        """Модификация рецепта."""
        if not (validated_data.get('ingredients')
                and validated_data.get('tags')):
            raise serializers.ValidationError(
                'Пропущено обязательное поле ингредиентов или тегов!'
            )
        ingredients = validated_data.pop('ingredients')
        IngredientRecipe.objects.filter(recipe=instance).delete()
        self.add_ingredients(
            ingredients,
            instance
        )
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        instance.image = validated_data.get(
            'image',
            instance.image
        )
        instance.name = validated_data.get(
            'name',
            instance.name
        )
        instance.text = validated_data.get(
            'text',
            instance.text
        )
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        instance.save()
        return instance


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор избранных рецептов."""

    id = serializers.PrimaryKeyRelatedField(
        source='recipe.id',
        read_only=True
    )
    name = serializers.ReadOnlyField(source='recipe.name')
    image = serializers.ImageField(
        source='recipe.image',
        read_only=True
    )
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = Favorite
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор списка покупок."""

    id = serializers.PrimaryKeyRelatedField(
        source='recipe.id',
        read_only=True
    )
    name = serializers.ReadOnlyField(source='recipe.name')
    image = serializers.ImageField(
        source='recipe.image',
        read_only=True
    )
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = ShoppingCart
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class RecipePresentitiveSerializer(serializers.ModelSerializer):
    """Сериализатор основных данных рецепта."""

    image = Base64ImageField(allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
