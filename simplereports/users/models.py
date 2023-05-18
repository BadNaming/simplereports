from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from users.managers import UserManager


class User(AbstractUser):
    """Кастомная модель пользователя"""

    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(
        'Имя',
        max_length=150)
    last_name = models.CharField(
        'Фамилия',
        max_length=150)
    phone_number = models.CharField(
        'Номер телефона',
        max_length=16)
    vk_client_id = models.CharField(
        'Client ID ВК',
        max_length=200,
        blank=True)
    vk_client_secret = models.CharField(
        'Client secret ВК',
        max_length=200,
        blank=True)

    username = None

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']

    def get_short_name(self):
        return self.first_name

    def natural_key(self):
        return self.first_name

    def __str__(self):
        return self.first_name
