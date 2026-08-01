import factory

from apps.staff.models import StaffMember

from tests.factories.accounts import UserFactory


class StaffMemberFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = StaffMember

    user = factory.SubFactory(
        UserFactory
    )

    personnel_number = factory.Sequence(
        lambda number: f"TEST-{number:06d}"
    )

    last_name = factory.Sequence(
        lambda number: f"Фамилия{number}"
    )
    first_name = factory.Sequence(
        lambda number: f"Имя{number}"
    )
    middle_name = ""

    gender = ""
    birth_date = None
    phone = ""
    email = factory.LazyAttribute(
        lambda obj: (
            f"{obj.personnel_number.lower()}"
            "@example.com"
        )
    )

    academic_degree = None
    academic_title = None
    degree_awarded_date = None
    title_awarded_date = None

    is_active = True
    notes = ""

    created_by = factory.SelfAttribute(
        "user"
    )
    updated_by = factory.SelfAttribute(
        "user"
    )