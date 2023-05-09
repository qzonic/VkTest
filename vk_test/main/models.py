from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """
    Модель пользователя
    """

    friends = models.ManyToManyField(
        'self',
        symmetrical=True,
        blank=True
    )


class Invitation(models.Model):
    """
    Модель приглашения в друзья
    """

    from_user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='sender'
    )
    to_user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='recipient'
    )
