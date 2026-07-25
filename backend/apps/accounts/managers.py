from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """
    Менеджер кастомной модели пользователя.

    В качестве идентификатора для входа используется username.
    """

    use_in_migrations = True

    def create_user(
        self,
        username: str,
        password: str | None = None,
        **extra_fields,
    ):
        if not username:
            raise ValueError(_("Имя пользователя обязательно."))

        username = self.model.normalize_username(username)

        email = extra_fields.get("email")
        if email:
            extra_fields["email"] = self.normalize_email(email)

        user = self.model(
            username=username,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(
        self,
        username: str,
        password: str | None = None,
        **extra_fields,
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(
                _("Суперпользователь должен иметь is_staff=True.")
            )

        if extra_fields.get("is_superuser") is not True:
            raise ValueError(
                _("Суперпользователь должен иметь is_superuser=True.")
            )

        return self.create_user(
            username=username,
            password=password,
            **extra_fields,
        )