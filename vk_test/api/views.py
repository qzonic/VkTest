from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, views, status

from .mixins import CreateMixin, ListMixin
from main.models import CustomUser, Invitation
from .serializers import (
    UserFriendsSerializer,
    InvitationSerializer,
    UsernameSerializer,
)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вьюскт для просмотра списка пользователей
    и друзей каждого пользователя.
    """

    lookup_field = 'username'
    queryset = CustomUser.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return UsernameSerializer
        return UserFriendsSerializer


class ListCreateModelViewSet(
    CreateMixin,
    ListMixin,
    viewsets.GenericViewSet
):
    pass


class InvitationViewSet(ListCreateModelViewSet):
    """
    ViewSet позволяет просматривать полученые заявки и
    отправлять заявки другим пользователям.
    """

    queryset = Invitation.objects.all()
    serializer_class = InvitationSerializer

    def get_queryset(self):
        return self.queryset.filter(to_user=self.request.user)

    @action(
        detail=False,
        methods=['get'],
        url_path='my'
    )
    def get_self_invitation(self, request):
        invitation = Invitation.objects.filter(
            from_user=request.user
        )
        if invitation.exists():
            serializer = self.serializer_class(invitation, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            data={'message': 'Вы еще не отправляли заявки!'},
            status=status.HTTP_204_NO_CONTENT)


class BaseAPIViewForInvitation(views.APIView):
    confirm = False

    def get_queryset(self, username):
        return get_object_or_404(
            Invitation,
            from_user__username=username,
            to_user=self.request.user
        )

    def get_message(self, username):
        return self.message.format(username)

    def patch(self, request, username):
        instance = self.get_queryset(username)
        data = {
            'message': self.get_message(username)
        }
        if self.confirm:
            self.request.user.friends.add(instance.from_user)
        instance.delete()
        return Response(data, self.STATUS)


class ConfirmInvitationAPIView(BaseAPIViewForInvitation):
    """
    Вьюха для подтверждения заявки
    """

    STATUS = status.HTTP_201_CREATED
    message = 'Вы стали другом с пользователем `{0}`'
    confirm = True


class DenyInvitationAPIView(BaseAPIViewForInvitation):
    """
    Вьюха для отклонения заявки
    """

    STATUS = status.HTTP_201_CREATED
    message = 'Вы отклонили заявку от пользователя `{0}`'


class CheckStatusAPIView(views.APIView):
    """
    Вьха для проверки статуса дружбы с пользователем
    """

    def get(self, request, username):
        messages = {
            'friends': {'message': 'Уже друзья!'},
            'outcoming': {'message': 'Есть исходящая заявка!'},
            'incoming': {'message': 'Есть входящая заявка!'},
            'nothing': {'message': 'Нет ничего!'}
        }
        to_user = get_object_or_404(
            CustomUser,
            username=username
        )
        if request.user.friends.filter(username=username).exists():
            return Response(messages['friends'], status.HTTP_200_OK)
        elif Invitation.objects.filter(
                from_user=request.user,
                to_user=to_user
        ).exists():
            return Response(messages['outcoming'], status.HTTP_200_OK)
        elif Invitation.objects.filter(
                from_user=to_user,
                to_user=request.user
        ).exists():
            return Response(messages['incoming'], status.HTTP_200_OK)
        else:
            return Response(messages['nothing'], status.HTTP_204_NO_CONTENT)


class DeleteFriendAPIView(views.APIView):
    """
    Вьюха для удаления пользователя из друзей
    """

    serializer_class = UsernameSerializer

    def delete(self, request, username):
        data = {
            'message': f'Пользователь `{username}` не ваш друг!'
        }
        stat = status.HTTP_404_NOT_FOUND

        if request.user.friends.filter(username=username).exists():
            to_user = get_object_or_404(
                CustomUser,
                username=username
            )
            data['message'] = f'Пользователь `{username}` удален из друзей!'
            request.user.friends.remove(to_user)
            stat = status.HTTP_204_NO_CONTENT
        return Response(data, stat)
