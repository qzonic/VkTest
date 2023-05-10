from rest_framework import status, mixins
from rest_framework.response import Response

from main.models import CustomUser
from .serializers import UsernameSerializer


class CreateMixin(mixins.CreateModelMixin):

    def create(self, request, *args, **kwargs):
        to_user = CustomUser.objects.filter(
            username=request.data.get('to_user')
        )
        invitation = self.queryset.filter(
            from_user=to_user.first(),
            to_user=self.request.user
        )
        if invitation.exists():
            self.request.user.friends.add(to_user.first())
            invitation.delete()
            return Response(
                {'message': 'Вы стали друзьями по обоюдным заявкам!'},
                status=status.HTTP_201_CREATED
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(from_user=self.request.user)


class ListMixin(mixins.ListModelMixin):

    def list(self, request, *args, **kwargs):
        invitation = self.get_queryset()
        if not invitation.exists():
            return Response(status=status.HTTP_204_NO_CONTENT)
        return super().list(request, *args, **kwargs)
