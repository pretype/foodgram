"""Модуль с определением команды manage.py для импорта продуктов в БД."""

from django.core.management.base import BaseCommand

from recipes.management.commands.import_data import import_data
from recipes.models import Ingredient


class Command(BaseCommand):
    """Команда управления импортом продуктов."""

    help = 'Импорт продуктов из .json файла.'

    def handle(self, *args, **options):
        return import_data('ingredients.json', Ingredient)
