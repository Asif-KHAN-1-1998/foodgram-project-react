from django.contrib.auth.models import AbstractUser
from django.db import models
from recipes import validators


class CustomUser(AbstractUser):
    """Модель пользователя."""

    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=False,
        null=False,
        verbose_name="Email пользователя",
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        null=False,
        verbose_name="Логин пользователя",
        validators=(validators.validate_username,),
    )
    first_name = models.CharField(
        max_length=150,
        blank=False,
        null=False,
        verbose_name="Имя пользователя",
    )
    last_name = models.CharField(
        max_length=150,
        blank=False,
        null=False,
        verbose_name="Фамилия пользователя",
    )
    password = models.CharField(
        max_length=150,
        blank=False,
        null=False,
        verbose_name="Пароль пользователя",
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        ordering = ("id",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username
