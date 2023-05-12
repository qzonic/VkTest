# Стек
<img src="https://img.shields.io/badge/Python-4169E1?style=for-the-badge"/> <img src="https://img.shields.io/badge/Django-008000?style=for-the-badge"/> <img src="https://img.shields.io/badge/DRF-800000?style=for-the-badge"/> <img src="https://img.shields.io/badge/Docker-00BFFF?style=for-the-badge"/> <img src="https://img.shields.io/badge/PostgreSQL-87CEEB?style=for-the-badge"/>

# Описание проекта:

**Проект VkTest**

Проект VkTest это сервис, в котором пользователи могут регистрироваться,
просматривать список других пользователей, отправлять им заявки в друзья,
принимать/отклонять заявки от других пользователей, просмотреть статус
дружбы с другим пользователем. 

Если два пользователя отправляею
друг другу заявки, то они автоматичесви становятся друзьями.

# Как запустить проект:

*Клонировать репозиторий и перейти в него в командной строке:*
```
https://github.com/qzonic/VkTest.git
```
```
cd VkTest/
```

*Теперь необходимо собрать Docker-контейнеры:*
```
docker-compose up -d
```

*После сборки контейнеров, нужно прописать следующие команды по очереди:*
```
docker-compose exec web python manage.py makemigrations main
```

```
docker-compose exec web python manage.py migrate
```

```
docker-compose exec web python manage.py createsuperuser
```

```
docker-compose exec web python manage.py collectstatic --no-input
```

*Теперь проект доступен по адресу:*
```
http://localhost/
```

*Эндпоинты для взаимодействия с API можно посмотетреть в документации по адресу:*
```
http://localhost/redoc/
```

# Примеры запросов к API:
В примерах для запроса к API используется библиотека requests.

### Регистрация:
```python
import requests

# URL для регистрации
url = "http://localhost/auth/users/"
data = {
    "username": "test_user_1",
    "password": "testpassword123"
}
response = requests.post(url, data=data)
```
*Ответ от сервиса*
```json
{
  "email": "", 
  "username": "test_user_1", 
  "id": 1
}
```

### Получение токена:
```python
url = "http://localhost/auth/jwt/create/"
# data таже, что и выше
response = requests.post(url, data=data)
```
*Ответ от сервиса*
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY4MzgwMjQ5MywianRpIjoiMjZkNzkwMWExYjZhNDJkMDgwNzIxZTY1YWQ4ZmIwNDgiLCJ1c2VyX2lkIjoyfQ.EnjwdfHNnE_BNWlw6-ez5jDMq5_UH5TiYIcMID2fLOU", 
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjgzODAyNDkzLCJqdGkiOiJmMDUzZjRlNzMyZWI0YzIwODFhYWY4OTUxOTNjYzE4MCIsInVzZXJfaWQiOjJ9.GK-KOPfLU6TMguDCikkR-QXg6znFamivSOrCMDo1SFE"
}
```

### Обновление токена:
```python
data = {
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY4MzgwMDEyNywianRpIjoiYTNlOTQ2M2M2ZGZkNDhmZTg1NTkwYTM0YThjZTVlMGYiLCJ1c2VyX2lkIjo3fQ.GCPzolNWPgM5M8gXzphpuJ7fBTPFQCFiz2B36fMWbRk",
}
url = "http://localhost/auth/jwt/refresh/"
response = requests.post(url, data=data)
```
*Ответ от сервиса*
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjgzODAyNTU1LCJqdGkiOiJhNTUwZGNiZDMxNzY0OGFjOWE0NGE1MTY0MWZkZDdjMiIsInVzZXJfaWQiOjJ9.9dgHgOccSpCBnm8CQn7hN_yBCBYhttE-AlUmuzLiQkw"
}
```

### Список пользователей:

Далее все действия будут выполняться от пользователя `test_user_1`

Предположим, что в сервисе зарегистрированы еще 4 пользователя.

```python
import requests


url = "http://localhost/api/v1/users/"
headers = {
    'Authorization': "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjgzODAyNTU1LCJqdGkiOiJhNTUwZGNiZDMxNzY0OGFjOWE0NGE1MTY0MWZkZDdjMiIsInVzZXJfaWQiOjJ9.9dgHgOccSpCBnm8CQn7hN_yBCBYhttE-AlUmuzLiQkw"
}
response = requests.get(url, headers=headers)
```
*Ответ от сервиса*
```json
[
  {"username": "test_user_1"}, 
  {"username": "test_user_2"}, 
  {"username": "test_user_3"}, 
  {"username": "test_user_4"},
  {"username": "test_user_5"}
]
```

### Отправить заявку:
```python
url = "http://localhost/api/v1/invitation/"
data = {
    "to_user": "test_user_2"
}
response = requests.post(url, headers=headers, data=data)
```
*Ответ от сервиса*
```json
{
  "from_user": "test_user_1",
  "to_user": "test_user_2"
}
```

### Исходящие заявки:
```python
url = "http://localhost/api/v1/invitation/my/"
response = requests.get(url, headers=headers)
```
*Ответ от сервиса*
```json
[
  {
    "from_user": "test_user_1",
    "to_user": "test_user_2"
  }
]
```

### Входящие заявки:

Представим, что пользователи `test_user_3` и `test_user_4` отправили нам заявки

```python
url = "http://localhost/api/v1/invitation/"
response = requests.get(url, headers=headers)
```
*Ответ от сервиса*
```json
[
  {
    "from_user": "test_user_3",
    "to_user": "test_user_1"
  },
  {
    "from_user": "test_user_4", 
    "to_user": "test_user_1"
  }
]
```

### Принять заявку:

Принимаем заявку от `test_user_3`

```python
url = "http://localhost/api/v1/confirm-invitation/test_user_3/"
response = requests.patch(url, headers=headers)
```
*Ответ от сервиса*
```json
{
  "message": "Вы стали другом с пользователем `test_user_3`"
}
```

### Отклонить заявку:

Отклоняем заявку от `test_user_4`

```python
url = "http://localhost/api/v1/deny-invitation/test_user_4/"
response = requests.patch(url, headers=headers)
```
*Ответ от сервиса*
```json
{
  "message": "Вы отклонили заявку от пользователя `test_user_4`"
}
```

### Друзья пользователя:

```python
url = "http://localhost/api/v1/users/test_user_1/"
response = requests.get(url, headers=headers)
```
*Ответ от сервиса*
```json
{
  "username": "test_user_1", 
  "friends": [
    "test_user_3"
  ]
}
```

### Статус дружбы:

Пользователю `test_user_2` мы отправили заявку;
Пользователь `test_user_3` у нас в друзьях;
Предположим, что пользователь `test_user_4` опять отправил нам заявку;

Статус с `test_user_2`
```python
url = "http://localhost/api/v1/check-status/test_user_2/"
response = requests.get(url, headers=headers)
```
*Ответ от сервиса*
```json
{
  "message": "Есть исходящая заявка!"
}
```
Статус с `test_user_3`
```python
url = "http://localhost/api/v1/check-status/test_user_3/"
response = requests.get(url, headers=headers)
```
*Ответ от сервиса*
```json
{
  "message": "Уже друзья!"
}
```
Статус с `test_user_4`
```python
url = "http://localhost/api/v1/check-status/test_user_4/"
response = requests.get(url, headers=headers)
```
*Ответ от сервиса*
```json
{
  "message": "Есть входящая заявка!"
}
```
Статус с `test_user_5`
```python
url = "http://localhost/api/v1/check-status/test_user_5/"
response = requests.get(url, headers=headers)
```
*Ответ от сервиса*
```json
{
  "message": "Нет ничего!"
}
```

### Удалить друга:

```python
url = "http://localhost/api/v1/delete-friends/test_user_3/"
response = requests.delete(url, headers=headers)
```
*Ответ от сервиса*
```
<Response [204]>
```

### Обоюдные заявки:

Предположим, что пользователь `test_user_5` отправил нам заявку и теперь мы отправляем ему заявку

```python
url = "http://localhost/api/v1/invitation/"
data = {
    "to_user": "test_user_5"
}
response = requests.post(url, headers=headers, data=data)
```
*Ответ от сервиса*
```json
{
  "message": "Вы стали друзьями по обоюдным заявкам!"
}
```

### Автор
[![telegram](https://img.shields.io/badge/Telegram-Join-blue)](https://t.me/qzonic)
