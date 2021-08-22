# Yatube
Социальная сеть для публикаций дневников.
В проекте используется пагинация постов и кэширование. Регистрация реализована с 
верификацией данных, сменой и восстановлением паролей через почту. 

## Стек технологий
Python 3.7.10, Django 3, 2, 3, SQLite3.

## Инструкция по развёртыванию
Создайте виртуальное окружение:
```bash
python -m venv venv
```
Активируйте его:
```bash
source venv/Scripts/activate
```
Установите зависимости:
```bash
pip install -r requirements.txt
```
Сделайте миграции:
```bash
python manage.py migrate
```
Создайте супер пользователя:
```bash
python manage.py createsuperuser
```
И запускайте сервер:
```bash
python manage.py runserver
```
