from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from users.managers import UserManager
from users.validators import validate_real_name, validate_phone_number


class User(AbstractUser):
    """Кастомная модель пользователя
    Attrs:
    - email: email пользователя, используется для входа в сервис
    - first_name: имя пользователя
    - last_name: фамилия пользователя
    - phone_number: номер телефона пользователя
    - vk_client_id: идентификатор, получаемый в поддержке вк
    - vk_client_secret: секрет, получаемый в поддержке вк
    - vk_client_token: персональный токен, для получения нужно отправить
    запрос к API ВК и передать vk_client_id и vk_client_secret
    """

    email = models.EmailField(_("email address"), unique=True)
    first_name = models.CharField(
        "Имя", max_length=150, validators=[validate_real_name]
    )
    last_name = models.CharField(
        "Фамилия", max_length=150, validators=[validate_real_name]
    )
    phone_number = models.CharField(
        "Номер телефона", max_length=16, validators=[validate_phone_number]
    )
    vk_client_id = models.CharField("Client ID ВК", max_length=200, null=True)
    vk_client_secret = models.CharField("Client secret ВК", max_length=1000, null=True)
    vk_client_token = models.CharField(
        "Токен доступа к API ВК", max_length=255, null=True
    )

    username = None

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "phone_number"]

    def get_short_name(self):
        return self.first_name

    def natural_key(self):
        return self.first_name

    def __str__(self):
        return self.first_name
