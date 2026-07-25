from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts.managers import UserManager


class User(AbstractUser):
    class InterfaceLanguage(models.TextChoices):
        RUSSIAN = "ru", _("Русский")
        UZBEK = "uz", _("O‘zbekcha")

    email = models.EmailField(
        _("Электронная почта"),
        blank=True,
    )
    middle_name = models.CharField(
        _("Отчество"),
        max_length=150,
        blank=True,
    )
    interface_language = models.CharField(
        _("Язык интерфейса"),
        max_length=2,
        choices=InterfaceLanguage.choices,
        default=InterfaceLanguage.RUSSIAN,
    )
    phone = models.CharField(
        _("Номер телефона"),
        max_length=30,
        blank=True,
    )
    avatar = models.ImageField(
        _("Фотография"),
        upload_to="users/avatars/%Y/%m/",
        blank=True,
        null=True,
    )
    must_change_password = models.BooleanField(
        _("Требуется сменить пароль"),
        default=False,
    )
    created_at = models.DateTimeField(
        _("Дата создания"),
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        _("Дата изменения"),
        auto_now=True,
    )

    objects = UserManager()

    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")
        ordering = ("last_name", "first_name", "username")

    def __str__(self) -> str:
        return self.get_full_name() or self.username

    @property
    def full_name(self) -> str:
        return " ".join(
            part
            for part in (
                self.last_name,
                self.first_name,
                self.middle_name,
            )
            if part
        )