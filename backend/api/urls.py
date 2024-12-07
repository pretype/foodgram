"""Модуль с маршрутизацией приложения API проекта Foodgram."""

from django.urls import include, path
from recipes.views import IngredientViewSet, RecipeViewSet, TagViewSet
from rest_framework.routers import DefaultRouter
from users.views import UserViewSet

app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register(r'users', UserViewSet)
router_v1.register(r'recipes', RecipeViewSet)
router_v1.register(r'tags', TagViewSet)
router_v1.register(r'ingredients', IngredientViewSet)

urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken'))
]
