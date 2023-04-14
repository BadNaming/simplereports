from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from users.managers import UserManager


class User(AbstractUser):
    """Кастомная модель пользователя"""

    email = models.EmailField(_('email address'), unique=True)
    username = None

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
