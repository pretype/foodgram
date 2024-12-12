"""Модуль с сериализаторами проекта Foodgram."""

from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from api.validators import ingredients_or_tags_validation
from recipes.constants import (DEFAULT_RECIPES_LIMIT_PARAM,
                               DEFAULT_RECIPES_LIMIT_VALUE, MIN_AMOUNT,
                               MIN_COOKING_TIME)
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Subscription, Tag, User)


class UserSerializer(DjoserUserSerializer):
    """Сериализатор пользователя."""

    is_subscribed = serializers.SerializerMethodField(
        read_only=True
    )
    avatar = Base64ImageField()

    class Meta(DjoserUserSerializer.Meta):
        model = User
        fields = (
            *DjoserUserSerializer.Meta.fields,
            'is_subscribed',
            'avatar'
        )

    def get_is_subscribed(self, author):
        """Проверяет подписку на пользователя."""
        current_user = self.context['request'].user
        return bool(
            current_user.is_authenticated
            and Subscription.objects.filter(
                user=current_user,
                author=author
            ).exists()
        )

    def validate(self, data):
        """Валидация аватара."""
        if not data.get('avatar'):
            raise serializers.ValidationError(
                'Не выбран пользовательский аватар!'
            )
        return data


class SubscriptionsSerializer(UserSerializer):
    """Сериализатор подписок."""

    recipes_count = serializers.ReadOnlyField(source='recipes.count')
    recipes = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            *UserSerializer.Meta.fields,
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, author):
        """Отдаёт список рецептов с возможностью лимитирования."""
        limit = int(
            self.context['request'].GET.get(
                DEFAULT_RECIPES_LIMIT_PARAM,
                DEFAULT_RECIPES_LIMIT_VALUE
            )
        )
        return RecipePresentitiveSerializer(
            author.recipes.all()[:limit],
            many=True
        ).data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор продуктов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор модели продукт-рецепт."""

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
        source='ingredients_in_recipe'
    )
    image = Base64ImageField()
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

    def get_is_favorited(self, recipe):
        """Проверяет избранность рецепта."""
        user = self.context['request'].user
        return (
            user.is_authenticated
            and Favorite.objects.filter(
                user=user,
                recipe=recipe
            ).exists()
        )

    def get_is_in_shopping_cart(self, recipe):
        """Проверяет включение рецепта в список покупок."""
        user = self.context['request'].user
        return (
            user.is_authenticated
            and ShoppingCart.objects.filter(
                user=user,
                recipe=recipe
            ).exists()
        )


class IngredientAddRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор добавления продукта в рецепт."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(min_value=MIN_AMOUNT)

    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'amount'
        )


class RecipeModificateSerializer(serializers.ModelSerializer):
    """Сериализатор добавления рецепта."""

    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = IngredientAddRecipeSerializer(
        many=True
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(min_value=MIN_COOKING_TIME)

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
        """Отдаёт или добавляет продукты в базу."""
        for _ingredient in ingredients:
            IngredientRecipe.objects.get_or_create(
                recipe=recipe,
                ingredient=_ingredient['id'],
                amount=_ingredient['amount']
            )

    def validate_tags(self, tags):
        """Валидация тегов рецепта."""
        ingredients_or_tags_validation(tags)
        return tags

    def validate_ingredients(self, ingredients):
        """Валидация продуктов рецепта."""
        _ingredients = [ing['id'] for ing in ingredients]
        ingredients_or_tags_validation(_ingredients)
        return ingredients

    def validate(self, data):
        """Валидация изображения."""
        if not data.get('image'):
            raise serializers.ValidationError(
                'Не выбрано изображение рецепта!'
            )
        return data

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
        recipe = super().create(validated_data)
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
                'Пропущено обязательное поле продуктов или тегов!'
            )
        ingredients = validated_data.pop('ingredients')
        IngredientRecipe.objects.filter(recipe=instance).delete()
        self.add_ingredients(
            ingredients,
            instance
        )
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        return super().update(instance, validated_data)


class RecipePresentitiveSerializer(serializers.ModelSerializer):
    """Сериализатор основных данных рецепта."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
