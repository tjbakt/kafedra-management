import factory
from django.contrib.auth import get_user_model


User = get_user_model()


class UserFactory(
    factory.django.DjangoModelFactory
):
    """
    Базовый пользователь проекта.

    Пароль по умолчанию:
    test-password-123
    """

    class Meta:
        model = User
        django_get_or_create = (
            "username",
        )

    username = factory.Sequence(
        lambda number: f"test_user_{number}"
    )
    email = factory.LazyAttribute(
        lambda obj: f"{obj.username}@example.com"
    )
    first_name = factory.Faker(
        "first_name",
        locale="ru_RU",
    )
    last_name = factory.Faker(
        "last_name",
        locale="ru_RU",
    )
    middle_name = ""
    phone = ""
    interface_language = (
        User.InterfaceLanguage.RUSSIAN
    )
    is_active = True
    is_staff = False
    is_superuser = False
    must_change_password = False

    @factory.post_generation
    def password(
        self,
        create,
        extracted,
        **kwargs,
    ):
        password = (
            extracted
            or "test-password-123"
        )

        self.set_password(password)

        if create:
            self.save(
                update_fields=("password",)
            )


class StaffUserFactory(UserFactory):
    is_staff = True


class SuperUserFactory(UserFactory):
    is_staff = True
    is_superuser = True