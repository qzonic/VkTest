from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet,
    InvitationViewSet,
    ConfirmInvitationAPIView,
    DenyInvitationAPIView,
    CheckStatusAPIView,
    DeleteFriendAPIView
)


router = DefaultRouter()

router.register('users', UserViewSet)
router.register('invitation', InvitationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('check-status/<str:username>/', CheckStatusAPIView.as_view(), name='check_status'),
    path('delete-friend/<str:username>/', DeleteFriendAPIView.as_view(), name='delete_friend'),
    path('confirm-invitation/<str:username>/', ConfirmInvitationAPIView.as_view(), name='confirm'),
    path('deny-invitation/<str:username>/', DenyInvitationAPIView.as_view(), name='deny'),
]
