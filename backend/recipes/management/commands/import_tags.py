"""Модуль с определением команды manage.py для импорта тегов в БД."""

from django.core.management.base import BaseCommand

from recipes.management.commands.import_data import import_data
from recipes.models import Tag


class Command(BaseCommand):
    """Команда управления импортом тегов."""

    help = 'Импорт тегов из .json файла.'

    def handle(self, *args, **options):
        return import_data('tags.json', Tag)
