"""Модуль с функцией импорта данных в БД проекта Foodgram."""

import json
import os

from django.conf import settings


def import_data(filename, model):
    """Загружает данные в модель."""
    file_path = os.path.join(settings.BASE_DIR, 'data', filename)
    data_file = open(file_path, 'r', encoding='UTF-8')
    data = json.loads(data_file.read())
    data_file.close()
    model.objects.bulk_create(
        (model(**tag_or_ing) for tag_or_ing in data),
        ignore_conflicts=True
    )
