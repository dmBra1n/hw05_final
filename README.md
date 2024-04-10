# YaTub

## Описание проекта

Социальная сеть YaTube для публикации постов и картинок.

Возможности проекта:
- Расширенная регистрация с возможностью управления профилем (используется переопределение модели User с помощью AbstractUser).
- Публикация записей с вложенными изображениями.
- Публикация записей в различных сообществах.
- Возможность комментировать записи других авторов.
- Функционал подписки на интересующих авторов.
- Лента с записями, на которые подписан пользователь.
- Использование template tags для отображения самых обсуждаемых и последних записей.
- Написаны тесты Unittest для проверки функциональности проекта.

#### Инструменты и стек:
[![Python](https://img.shields.io/badge/-Python-464641?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-464646?style=flat-square&logo=django)](https://www.djangoproject.com/)
[![Unittest](https://img.shields.io/badge/Unittest-464646?style=flat-square&logo=pytest)](https://docs.pytest.org/en/6.2.x/)
[![SQLite3](https://img.shields.io/badge/-SQLite3-464646?style=flat-square&logo=SQLite)](https://www.sqlite.org/)

## Локальный запуск проекта
1. Склонировать репозиторий
2. Установить зависимости с помощью `pip install -r requirements.txt`
3. В корне проекта создать и заполнить _.env_
    ```env
    SECRET_KEY=<django_secret_key>
    ```
4. Выполнить миграции и собрать статику
    ```
    python manage.py migrate
    python manage.py collectstatic
    ```
5. Создать суперпользователя Django: `python manage.py createsuperuser`
6. Запустить проект: `python manage.py runserver`

  ## Автор
Вадим Миронов - [ссылка на GitHub](https://github.com/dmBra1n)
