"""Модуль с настройками пагинации проекта Foodgram."""

from rest_framework.pagination import PageNumberPagination

from .constants import DEFAULT_PAGE_LIMIT_PARAM, DEFAULT_PAGE_SIZE


class StandardResultsSetPagination(PageNumberPagination):
    """Настройка пагинации."""

    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = DEFAULT_PAGE_LIMIT_PARAM
