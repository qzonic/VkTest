from django.contrib import admin

from .models import CustomUser, Invitation


admin.site.register(CustomUser)
# admin.site.register(FriendShip)
admin.site.register(Invitation)
