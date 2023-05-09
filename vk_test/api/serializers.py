from rest_framework import serializers
from main.models import CustomUser, Invitation


class UsernameSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ('username',)


class UserFriendsSerializer(serializers.ModelSerializer):

    friends = serializers.SlugRelatedField(
        slug_field='username',
        many=True,
        read_only=True
    )

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'friends',
        )


class InvitationSerializer(serializers.ModelSerializer):
    from_user = serializers.SlugRelatedField(
        slug_field='username',
        default=serializers.CurrentUserDefault(),
        read_only=True
    )
    to_user = serializers.SlugRelatedField(
        slug_field='username',
        queryset=CustomUser.objects.all()
    )

    class Meta:
        model = Invitation
        fields = ('from_user', 'to_user')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Invitation.objects.all(),
                fields=['from_user', 'to_user'],
                message='Вы уже отправили заявку этому пользователю!'
            )
        ]

    def validate(self, attrs):
        current_user = self.context['request'].user
        if attrs['to_user'] in current_user.friends.all():
            raise serializers.ValidationError(
                'Вы уже друзья!'
            )
        return attrs

    def validate_to_user(self, value):
        current_user = self.context['request'].user
        if current_user == value:
            raise serializers.ValidationError(
                'Нельзя отправить завку себе!'
            )
        return value
