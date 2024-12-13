"""Модуль с настройками пагинации проекта Foodgram."""

from recipes.constants import DEFAULT_PAGE_LIMIT_PARAM, DEFAULT_PAGE_SIZE

from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """Настройка пагинации."""

    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = DEFAULT_PAGE_LIMIT_PARAM
