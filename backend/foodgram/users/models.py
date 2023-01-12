from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомная модель для пользователей"""

    USER = 'user'
    ADMIN = 'admin'

    ROLE_CHOICES = (
        (USER, 'User'),
        (ADMIN, 'Admin')
    )
    username = models.CharField(
        unique=True,
        verbose_name='username',
        max_length=100
    )
    first_name = models.CharField(
        verbose_name='first_name',
        max_length=150
    )
    last_name = models.CharField(
        verbose_name='last_name',
        max_length=150
    )
    email = models.EmailField(
        unique=True,
        verbose_name='Адрес электронной почты'
    )
    role = models.CharField(
        verbose_name='role',
        choices=ROLE_CHOICES,
        default=USER,
        max_length=20
    )

    REQUIRED_FIELDS = (username, email, first_name, last_name)

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        ordering = ('-id',)
        verbose_name = 'User'
        verbose_name_plural = 'Users'
