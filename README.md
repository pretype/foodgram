# Проект 12-го спринта Foodgram
##### @Яндекс Практикум

Проект доступен по ссылке: [Главная веб-страница проекта](https://fdgrm-071224.hopto.org)
Документация API проекта доступна по ссылке: [Документация API проекта](https://fdgrm-071224.hopto.org/api/docs/)

***

## Workflow status badge (Бейдж сборки)

[![Main Foodgram workflow](https://github.com/pretype/foodgram/actions/workflows/main.yml/badge.svg)](https://github.com/pretype/foodgram/actions/workflows/main.yml)

***

## Использованные технологии
```
Python
Django
Django REST framework
PostgreSQL
Nginx
Docker
Docker Hub
Git
GitHub
```

Иные использованные технологии и их версии, указаны в файле "requirements.txt" в корне проекта.

***

## Описание

Проект Foodgram создан для настоящих гурманов. На сайте проекта, пользователи могут делиться описаниями любимых блюд, а также рецептами их приготовления. Каждый авторизованный пользователь волен добавить свой рецепт на всеобщее обозрение. Существует возможность добавлять понравившиеся рецепты в избранное, а также подписываться на наиболее толковых авторов. Рецепты выбранные для приготовления можно добавить в список покупок, а затем получить файл со списком и кол-вом ингредиентов, необходимых для претворения блюда в жизнь. Также реализованы другие полезные и приятные функции.

***

## Локальные установка и запуск проекта

<details>
  <summary><b<strong>Локальная установка и запуск проекта Foodgram</strong></b></summary>

1. Убедитесь, что у Вас развернуты виртуальная машина и Docker

2. Клонируйте проект foodgram с GitHub:
  ```bash
  git clone https://github.com/pretype/foodgram
  ```

3. Перейдите в локальную директорию проекта foodgram:
  ```bash
  cd foodgram
  ```

4. Из корневой директории проекта создайте файл ".env", внесите в него переменные, указанные ниже, и их значения:
```
SECRET_KEY
ALLOWED_IP
ALLOWED_DOMAIN
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_DB
DB_HOST
DB_PORT
```

5. Из корневой директории запустите Docker-compose

  ```bash
  docker compose up
  ```

6. В другом терминале, в корневой директории, выполните миграции, сбор и копировании статики

  ```bash
  docker compose -f docker-compose.yml exec backend python manage.py makemigrations
  docker compose -f docker-compose.yml exec backend python manage.py migrate
  docker compose -f docker-compose.yml exec backend python manage.py collectstatic
  docker compose -f docker-compose.yml exec backend cp -r /app/collected_static/. /backend_static
  ```

Проект будет доступен по веб-адресу:
[Главная страница проекта](http://localhost:8000/)

</details>

***

## Примеры
### Пример API POST-запроса от авторизованного пользователя

<details>
  <summary><b<strong>Пример POST-запроса к /api/recipes/</strong></b></summary>

<details>
  <summary>Тело запроса:</summary>

```
{
  "ingredients": [
    {
      "id": 1,
      "amount": 5
    },
    {
      "id": 2,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "Нечто съедобное (это не точно)",
  "text": "Приготовьте как нибудь эти ингредиеты",
  "cooking_time": 5
}

```
</details>

Статус ответа: 201 CREATED.
<details>
  <summary>Тело ответа на запрос:</summary>

```
{
    "id": 1,
    "author": {
        "id": 3,
        "email": "second_user@email.org",
        "username": "second-user",
        "first_name": "Андрей",
        "last_name": "Макаревский",
        "is_subscribed": false,
        "avatar": null
    },
    "name": "Нечто съедобное (это не точно)",
    "text": "Приготовьте как нибудь эти ингредиеты",
    "tags": [
        {
            "id": 1,
            "name": "завтрак",
            "slug": "brkfst"
        },
        {
            "id": 2,
            "name": "обед",
            "slug": "lnch"
        }
    ],
    "ingredients": [
        {
            "id": 1,
            "name": "хлеб",
            "measurement_unit": "шт.",
            "amount": 5
        },
        {
            "id": 3,
            "name": "соль",
            "measurement_unit": "г.",
            "amount": 10
        }
    ],
    "image": "http://localhost/media/recipes/images/temp_Vlil6Ir.png",
    "cooking_time": 5,
    "is_favorited": false,
    "is_in_shopping_cart": false
}

```

</details>

</details>

<details>
  <summary><b<strong>Пример ответа на GET-запрос к /api/users/</strong></b></summary>

```
{
    "count": 4,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "email": "a@a.aa",
            "username": "A",
            "first_name": "A",
            "last_name": "A",
            "is_subscribed": false,
            "avatar": "http://localhost/media/users/avatars/temp_IQGvEfo.png"
        },
        {
            "id": 3,
            "email": "second_user@email.org",
            "username": "second-user",
            "first_name": "Андрей",
            "last_name": "Макаревский",
            "is_subscribed": false,
            "avatar": null
        },
        {
            "id": 4,
            "email": "third-user@user.ru",
            "username": "third-user-username",
            "first_name": "Гордон",
            "last_name": "Рамзиков",
            "is_subscribed": false,
            "avatar": null
        },
        {
            "id": 2,
            "email": "vivanov@yandex.ru",
            "username": "vasya.ivanov",
            "first_name": "Вася",
            "last_name": "Иванов",
            "is_subscribed": false,
            "avatar": null
        }
    ]
}

```

</details>

Вся информация по API есть в документации по веб-адресу локально запущенного проекта: 
[Документация к API проекта](http://localhost:8000/api/docs/)

***

## Автор
### Шарафетдинов Д. Р. ([pretype](https://github.com/pretype))

