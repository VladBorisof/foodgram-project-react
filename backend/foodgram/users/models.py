from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомная модель для пользователей"""

    email = models.EmailField(
        unique=True,
        verbose_name='Адрес электронной почты'
    )
