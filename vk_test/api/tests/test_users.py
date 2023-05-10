from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from main.models import CustomUser, Invitation


User = get_user_model()


class TestUser(APITestCase):

    @classmethod
    def setUpClass(cls):
        super(TestUser, cls).setUpClass()
        cls.first_user = User.objects.create(
            username='first_user',
            email='first_user@mail.ru'
        )
        cls.second_user = User.objects.create(
            username='second_user',
            email='second_user@mail.ru'
        )
        cls.third_user = User.objects.create(
            username='third_user',
            email='third_user@mail.ru'
        )
        cls.fours_user = User.objects.create(
            username='fours_user',
            email='fours_user@mail.ru'
        )
        cls.fifth_user = User.objects.create(
            username='fifth_user',
            email='fifth_user@mail.ru'
        )

        cls.url_users_list = '/api/v1/users/'
        cls.url_user_friends = '/api/v1/users/first_user/'

    def setUp(self):
        self.authorized_client = APIClient()
        token = RefreshToken.for_user(self.first_user)
        self.authorized_client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(token.access_token)}')

    def test_users_list(self):

        response = self.authorized_client.get(self.url_users_list)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            f'Проверьте, что GET-запрос на эндпоинт `{self.url_users_list}`, '
            'возвращает ответ со статусом 200.'
        )

        self.assertIsInstance(
            response.json(),
            list,
            f'Проверьте, что GET-запрос на эндпоинт `{self.url_users_list}`, '
            'возвращает ответ список пользователей.'
        )

        users = [
            self.first_user.username,
            self.second_user.username,
            self.third_user.username,
            self.fours_user.username,
            self.fifth_user.username
        ]
        for field in response.json():
            self.assertIn(
                field['username'],
                users,
                f'Проверьте, что GET-запрос на эндпоинт `{self.url_users_list}`, '
                'возвращает ответ список существующих пользователей.'
            )

    def test_friends_list(self):

        self.first_user.friends.add(self.second_user)

        response = self.authorized_client.get(self.url_user_friends)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            f'Проверьте, что GET-запрос на эндпоинт `{self.url_user_friends}`, '
            'возвращает ответ со статусом 200.'
        )

        self.assertIn(
            self.second_user.username,
            response.json()['friends'],
            f'Проверьте, что GET-запрос на эндпоинт `{self.url_user_friends}`, '
            'возвращает добавленных в друзья пользователей.'
        )

        self.assertNotIn(
            self.third_user.username,
            response.json()['friends'],
            f'Проверьте, что GET-запрос на эндпоинт `{self.url_user_friends}`, '
            'не возвращает не добавленных в друзья пользователей.'
        )

    def test_check_status(self):
        self.first_user.friends.add(self.second_user)

        Invitation.objects.create(
            from_user=self.first_user,
            to_user=self.third_user
        )

        Invitation.objects.create(
            from_user=self.fours_user,
            to_user=self.first_user
        )

        url_check_status = reverse(
            'check_status',
            kwargs={'username': self.second_user.username}
        )
        response = self.authorized_client.get(url_check_status)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            f'Проверьте, что GET-запрос на эндпоинт `{url_check_status}`, '
            'возвращает ответ со статусом 200.'
        )
        self.assertEqual(
            response.json()['message'],
            'Уже друзья!',
            f'Проверьте, что GET-запрос на эндпоинт `{url_check_status}`, '
            'возвращает для пользователя, который в друзьях, ответ `Уже друзья!`.'
        )

        url_check_status = reverse(
            'check_status',
            kwargs={'username': self.third_user.username}
        )
        response = self.authorized_client.get(url_check_status)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            f'Проверьте, что GET-запрос на эндпоинт `{url_check_status}`, '
            'возвращает ответ со статусом 200.'
        )
        self.assertEqual(
            response.json()['message'],
            'Есть исходящая заявка!',
            f'Проверьте, что GET-запрос на эндпоинт `{url_check_status}`, '
            'возвращает для пользователя, которому отправленна заявка, ответ `Есть исходящая заявка!`.'
        )

        url_check_status = reverse(
            'check_status',
            kwargs={'username': self.fours_user.username}
        )
        response = self.authorized_client.get(url_check_status)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            f'Проверьте, что GET-запрос на эндпоинт `{url_check_status}`, '
            'возвращает ответ со статусом 200.'
        )
        self.assertEqual(
            response.json()['message'],
            'Есть входящая заявка!',
            f'Проверьте, что GET-запрос на эндпоинт `{url_check_status}`, '
            'возвращает для пользователя, которому отправленна заявка, ответ `Есть входящая заявка!`.'
        )

        url_check_status = reverse(
            'check_status',
            kwargs={'username': self.fifth_user.username}
        )
        response = self.authorized_client.get(url_check_status)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            f'Проверьте, что GET-запрос на эндпоинт `{url_check_status}`, '
            'возвращает ответ со статусом 200.'
        )
        self.assertEqual(
            response.data['message'],
            'Нет ничего!',
            f'Проверьте, что GET-запрос на эндпоинт `{url_check_status}`, '
            'возвращает для пользователя, которому отправленна заявка, ответ `Нет ничего!`.'
        )

    def test_delete_invalid_friend(self):
        url_delete = reverse(
            'delete_friend',
            kwargs={'username': self.second_user.username}
        )

        response = self.authorized_client.delete(url_delete)
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            f'Проверьте, что DELETE-запрос на эндпоинт `{url_delete}`, '
            'возвращает ответ со статусом 404, если пользователь не в друзьях.'
        )

        self.assertEqual(
            response.json()['message'],
            f'Пользователь `{self.second_user.username}` не ваш друг!',
            f'Проверьте, что DELETE-запрос на эндпоинт `{url_delete}`, '
            f'возвращает ответ `Пользователь `{self.second_user.username}` не ваш друг!`.'
        )

    def test_delete_valid_friend(self):
        url_delete = reverse(
            'delete_friend',
            kwargs={'username': self.second_user.username}
        )

        self.first_user.friends.add(self.second_user)

        response = self.authorized_client.delete(url_delete)
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
            f'Проверьте, что DELETE-запрос на эндпоинт `{url_delete}`, '
            'возвращает ответ со статусом 204, если пользователь был в друзьях.'
        )


