### Описание проекта:

**Проект VkTest**

Проект VkTest это сервис, в котором пользователи могут регистрироваться,
просматривать список других пользователей, отправлять им заявки в друзья,
принимать/отклонять заявки от других пользователей, просмотреть статус
друюбы с другим пользователем. 

Если два пользователя отправляею
друг другу заявки, то они автоматичесви становятся друзьями.

### Как запустить проект:

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
docker-compose exec web python manage.py makemigrations
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

[README.md](README.md)
*Теперь проект доступен по адресу:*
```
http://localhost/
```

*Эндпоинты для взаимодействия с API можно посмотетреть по адресу:*
```
http://localhost/redoc/
```

### Примеры запросов к API:
В примерах для запроса к API используется библиотека requests.

*Регистрация:*
```python
import requests

# URL для регистрации
url = "http://localhost/api/v1/auth/signup/"
data = {
    "username": "test_user",
    "email": "testuser@mail.ru"
}
response = requests.post(url, data=data)
```
