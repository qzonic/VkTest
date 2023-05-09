from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from main.models import CustomUser, Invitation


User = get_user_model()


class TestInvitation(APITestCase):

    @classmethod
    def setUpClass(cls):
        super(TestInvitation, cls).setUpClass()
        cls.first_user = User.objects.create(
            username='first_user',
        )
        cls.second_user = User.objects.create(
            username='second_user',
        )

        cls.url_send_invitation = reverse('invitation-list')
        cls.url_outcoming_invitation = reverse('invitation-get-self-invitation')
        cls.url_deny_invitation = reverse(
            'deny',
            kwargs={'username': cls.second_user.username}
        )
        cls.url_deny_invitation_nonexistent = reverse(
            'deny',
            kwargs={'username': 'nonexistent'}
        )
        cls.url_confirm_invitation = reverse(
            'confirm',
            kwargs={'username': cls.second_user.username}
        )
        cls.url_confirm_invitation_nonexistent = reverse(
            'confirm',
            kwargs={'username': 'nonexistent'}
        )

    def setUp(self):
        self.guest_client = APIClient()

        self.authorized_client = APIClient()
        first_user_token = RefreshToken.for_user(self.first_user)
        self.authorized_client.credentials(HTTP_AUTHORIZATION=f'Bearer {first_user_token.access_token}')

        self.second_authorized_client = APIClient()
        second_user_token = RefreshToken.for_user(self.second_user)
        self.second_authorized_client.credentials(HTTP_AUTHORIZATION=f'Bearer {second_user_token.access_token}')

    def test_invitation_from_guest(self):
        data = {
            'to_user': 'user'
        }
        response = self.guest_client.post(self.url_send_invitation, data)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            f'Проверьте, что POST-запрос на эндпоинт `{self.url_send_invitation}` без токена, '
            'возвращает ответ со статусом 401.'
        )

    def test_send_invitation_to_nonexistent_user(self):
        data = {
            'to_user': 'nonexistent_user'
        }

        response = self.authorized_client.post(self.url_send_invitation, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            f'Проверьте, что POST-запрос на эндпоинт `{self.url_send_invitation}` '
            'с некорректными данными от авторизованного пользователя, '
            'возвращает ответ со статусом 400.'
        )

    def test_send_invitation_to_existent_user(self):
        data = {
            'to_user': self.second_user.username
        }
        invitation_count = Invitation.objects.count()
        response = self.authorized_client.post(self.url_send_invitation, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            f'Проверьте, что POST-запрос на эндпоинт `{self.url_send_invitation}` '
            'с корректными данными от авторизованного пользователя, '
            'возвращает ответ со статусом 201.'
        )

        self.assertEqual(
            Invitation.objects.count(),
            invitation_count + 1,
            f'Проверьте, что POST-запрос на эндпоинт `{self.url_send_invitation}` '
            'с корректными данными от авторизованного пользователя, '
            'создает заявку.'
        )

        response = self.authorized_client.post(self.url_send_invitation, data)
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            f'Проверьте, что повторный POST-запрос на эндпоинт `{self.url_send_invitation}` '
            'от авторизованного пользователя c заявкой другу, '
            'возвращается ответ со статусом 400.'
        )

    def test_send_invitation_to_yourself(self):
        data = {
            'to_user': self.second_user.username
        }
        invitation_count = Invitation.objects.count()
        response = self.second_authorized_client.post(self.url_send_invitation, data)
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            f'Проверьте, что POST-запрос на эндпоинт `{self.url_send_invitation}` '
            'от авторизованного пользователя c заявкой себе, '
            'возвращается ответ со статусом 400.'
        )

        self.assertEqual(
            Invitation.objects.count(),
            invitation_count,
            f'Проверьте, что POST-запрос на эндпоинт `{self.url_send_invitation}` '
            'от авторизованного пользователя с заявкой себе, '
            'заявка не создается.'
        )

    def test_send_invitation_to_friend(self):
        self.first_user.friends.add(self.second_user)

        data = {
            'to_user': self.second_user.username
        }

        response = self.authorized_client.post(self.url_send_invitation, data)
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            f'Проверьте, что POST-запрос на эндпоинт `{self.url_send_invitation}` '
            'от авторизованного пользователя с своему другу, '
            'возвращается ответ со ствтусом 400.'
        )

    def test_incoming_invitation_with_valid_data(self):
        data = {
            'to_user': self.first_user.username
        }
        response = self.second_authorized_client.post(self.url_send_invitation, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            f'Проверьте, что POST-запрос на эндпоинт `{self.url_send_invitation}` '
            'с корректными данными от авторизованного пользователя, '
            'возвращает ответ со статусом 201.'
        )

        new_invitation = Invitation.objects.filter(
            from_user=self.second_user,
            to_user=self.first_user
        )

        self.assertTrue(
            new_invitation.exists(),
            f'Проверьте, что POST-запрос на эндпоинт `{self.url_send_invitation}` '
            'с корректными данными от авторизованного пользователя, '
            'отправляет заявку другому пользователю.'
        )

        response = self.second_authorized_client.get(self.url_send_invitation)
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
            f'Проверьте, что POST-запрос на эндпоинт `{self.url_send_invitation}` '
            'от авторизованного пользователя, вовращает ответ со статусом 204.'
        )

        response = self.authorized_client.get(self.url_send_invitation)
        self.assertEqual(
            response.json()[0]['to_user'],
            data['to_user'],
            f'Проверьте, что GET-запрос на эндпоинт `{self.url_send_invitation}` '
            'от авторизованного пользователя, возвращает входящие заявки при их наличии.'
        )

    def test_incoming_invitation_with_invalid_data(self):
        data = {
            'to_user': 'invalid_user'
        }
        response = self.second_authorized_client.post(self.url_send_invitation, data)
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            f'Проверьте, что POST-запрос на эндпоинт `{self.url_send_invitation}` '
            'с некорректными данными от авторизованного пользователя, '
            'возвращает ответ со статусом 400.'
        )

        new_invitation = Invitation.objects.filter(
            from_user=self.second_user,
            to_user=self.first_user
        )

        self.assertFalse(
            new_invitation.exists(),
            f'Проверьте, что POST-запрос на эндпоинт `{self.url_send_invitation}` '
            'с некорректными данными от авторизованного пользователя, '
            'не отправляет заявку другому пользователю.'
        )

    def test_outcoming_invitation_with_valid_data(self):
        data = {
            'to_user': self.first_user.username
        }
        response_post = self.second_authorized_client.post(self.url_send_invitation, data)
        self.assertEqual(
            response_post.status_code,
            status.HTTP_201_CREATED,
            f'Проверьте, что POST-запрос на эндпоинт `{self.url_send_invitation}` '
            'с корректными данными от авторизованного пользователя, '
            'возвращает ответ со статусом 201.'
        )

        response_get = self.second_authorized_client.get(self.url_outcoming_invitation)
        self.assertEqual(
            response_get.status_code,
            status.HTTP_200_OK,
            f'Проверьте, что GET-запрос на эндпоинт `{self.url_outcoming_invitation}` '
            'от авторизованного пользователя, возвращает ответ со статусом 200 '
            'при наличии исходящих заявок.'
        )

    def test_outcoming_invitation_with_invalid_data(self):
        data = {
            'to_user': 'invalid_user'
        }
        response = self.second_authorized_client.post(self.url_send_invitation, data)
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            f'Проверьте, что POST-запрос на эндпоинт `{self.url_send_invitation}` '
            'с некорректными данными от авторизованного пользователя, '
            'возвращает ответ со статусом 400.'
        )

        response = self.second_authorized_client.get(self.url_outcoming_invitation)
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
            f'Проверьте, что GET-запрос на эндпоинт `{self.url_outcoming_invitation}` '
            'от авторизованного пользователя, возвращает ответ со статусом 204 '
            'при их отсутсвии.'
        )

        new_invitation = Invitation.objects.filter(
            from_user=self.second_user,
            to_user=self.first_user
        )
        self.assertFalse(
            new_invitation.exists(),
            f'Проверьте, что POST-запрос на эндпоинт `{self.url_send_invitation}` '
            'с некорректными данными от авторизованного пользователя, '
            'не отправляет заявку другому пользователю.'
        )

    def test_confirm_nonexistent_invitation(self):

        friends_count = self.first_user.friends.count()

        response = self.authorized_client.patch(self.url_confirm_invitation_nonexistent)
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            f'Проверьте, что PATCH-запрос на эндпоинт `{self.url_confirm_invitation_nonexistent}` '
            'с некорректными данными от авторизованного пользователя, '
            'возвращает ответ со статусом 404.'
        )

        self.assertEqual(
            self.first_user.friends.count(),
            friends_count,
            f'Проверьте, что PATCH-запрос на эндпоинт `{self.url_confirm_invitation_nonexistent}` '
            'с некорректными данными от авторизованного пользователя, '
            'не добавляет пользователей в друзья.'
        )

    def test_confirm_existent_invitation(self):
        friends_count = self.first_user.friends.count()

        data = {
            'to_user': self.first_user.username
        }

        response = self.second_authorized_client.post(
            self.url_send_invitation, data
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            f'Проверьте, что POST-запрос на эндпоинт `{self.url_send_invitation}` '
            'с корректными данными от авторизованного пользователя, '
            'возвращает ответ со статусом 201.'
        )

        response = self.authorized_client.patch(self.url_confirm_invitation)
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            f'Проверьте, что PATCH-запрос на эндпоинт `{self.url_confirm_invitation}` '
            'от авторизованного пользователя, возвращает ответ со статусом 201 '
            'при подтверждении существующей заявки.'
        )

        self.assertEqual(
            self.first_user.friends.count(),
            friends_count + 1,
            f'Проверьте, что PATCH-запрос на эндпоинт `{self.url_confirm_invitation}` '
            'от авторизованного пользователя добавляет ему друзей.'
        )

        self.assertEqual(
            self.first_user.friends.filter(username=self.second_user.username).first(),
            self.second_user,
            f'Проверьте, что PATCH-запрос на эндпоинт `{self.url_confirm_invitation}` '
            'от авторизованного пользователя, добавляеет ему в друзья '
            f'пользователя с username={self.second_user.username}.'
        )

    def test_deny_nonexistent_invitation(self):

        friends_count = self.first_user.friends.count()

        response = self.authorized_client.patch(self.url_deny_invitation_nonexistent)
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            f'Проверьте, что PATCH-запрос на эндпоинт `{self.url_deny_invitation_nonexistent}` '
            'с некорректными данными от авторизованного пользователя, '
            'возвращает ответ со статусом 404.'
        )

        self.assertEqual(
            self.first_user.friends.count(),
            friends_count,
            f'Проверьте, что PATCH-запрос на эндпоинт `{self.url_deny_invitation_nonexistent}` '
            'с некорректными данными от авторизованного пользователя, '
            'не добавляет пользователей в друзья.'
        )

    def test_deny_existent_invitation(self):
        friends_count = self.first_user.friends.count()
        data = {
            'to_user': self.first_user.username
        }

        response = self.second_authorized_client.post(
            self.url_send_invitation, data
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            f'Проверьте, что POST-запрос на эндпоинт `{self.url_send_invitation}` '
            'с корректными данными от авторизованного пользователя, '
            'возвращает ответ со статусом 201.'
        )

        response = self.authorized_client.patch(self.url_deny_invitation)
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            f'Проверьте, что PATCH-запрос на эндпоинт `{self.url_deny_invitation}` '
            'от авторизованного пользователя, возвращает ответ со статусом 201 '
            'при отклонении существующей заявки.'
        )

        self.assertEqual(
            self.first_user.friends.count(),
            friends_count,
            f'Проверьте, что PATCH-запрос на эндпоинт `{self.url_deny_invitation}` '
            'от авторизованного пользователя не добавляет ему друзей.'
        )

        self.assertFalse(
            self.first_user.friends.filter(username=self.second_user.username).exists(),
            f'Проверьте, что PATCH-запрос на эндпоинт `{self.url_deny_invitation}` '
            'от авторизованного пользователя-1, не добавляеет ему в друзья '
            f'пользователя с username={self.second_user.username}.'
        )

    def test_add_friend_when_mutual_invitation(self):
        data = {
            'to_user': self.first_user.username
        }

        response = self.second_authorized_client.post(
            self.url_send_invitation, data
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            f'Проверьте, что POST-запрос на эндпоинт `{self.url_send_invitation}` '
            'с корректными данными от авторизованного пользователя, '
            'возвращает ответ со статусом 201.'
        )

        self.assertFalse(
            self.second_user.friends.filter(username=self.first_user.username).exists(),
            f'Проверьте, что POST-запрос на эндпоинт `{self.url_send_invitation}` '
            'от авторизованного пользователя-2, не добавляеет ему в друзья '
            f'пользователя с username={self.first_user.username}.'
        )

        data = {
            'to_user': self.second_user.username
        }

        response = self.authorized_client.post(
            self.url_send_invitation, data
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            f'Проверьте, что POST-запрос на эндпоинт `{self.url_send_invitation}` '
            'с корректными данными от авторизованного пользователя, '
            'возвращает ответ со статусом 201.'
        )

        self.assertEqual(
            self.first_user.friends.filter(username=self.second_user.username).first(),
            self.second_user,
            'Проверьте, что  - если пользователь1 отправляет заявку в друзья пользователю2, '
            'а пользователь2 отправляет заявку пользователю1, то они автоматом '
            'становятся друзьями, их заявки автоматом принимаются.'
        )



