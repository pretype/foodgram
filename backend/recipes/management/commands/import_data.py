"""Модуль с функцией импорта данных в БД проекта Foodgram."""

import json
import os
from contextlib import suppress

from django.db.utils import IntegrityError

from recipes.constants import DATA_STORAGE_PATH


def import_data(filename, model):
    """Загружает данные в модель."""
    file_path = os.path.join(DATA_STORAGE_PATH, filename)
    data_file = open(file_path, 'r', encoding='UTF-8')
    data = json.loads(data_file.read())
    data_file.close()
    with suppress(IntegrityError):
        model.objects.bulk_create(
            model(**tag_or_ing) for tag_or_ing in data
        )
