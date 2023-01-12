from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class UsersAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role')
    search_fields = ('first_name', 'email')
    fieldsets = (
        ('User', dict(fields=('username', 'password', 'email', 'first_name',
                              'last_name', 'role',
                              'last_login', 'date_joined'))),
    )
    list_filter = ('first_name', 'email')
