import factory

from apps.organizations.models import (
    Department,
    Faculty,
    University,
)

from tests.factories.accounts import (
    UserFactory,
)


class UniversityFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = University

    code = factory.Sequence(
        lambda number: f"UNI-{number:04d}"
    )
    name_ru = factory.Sequence(
        lambda number: (
            f"Тестовый университет {number}"
        )
    )
    name_uz = factory.Sequence(
        lambda number: (
            f"Test universiteti {number}"
        )
    )
    short_name_ru = factory.Sequence(
        lambda number: f"ТУ-{number}"
    )
    short_name_uz = factory.Sequence(
        lambda number: f"TU-{number}"
    )
    is_active = True
    sort_order = 0

    address_ru = ""
    address_uz = ""
    phone = ""
    email = factory.Sequence(
        lambda number: (
            f"university{number}@example.com"
        )
    )
    website = ""

    created_by = factory.SubFactory(
        UserFactory
    )
    updated_by = factory.SelfAttribute(
        "created_by"
    )


class FacultyFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = Faculty

    university = factory.SubFactory(
        UniversityFactory
    )

    code = factory.Sequence(
        lambda number: f"FAC-{number:04d}"
    )
    name_ru = factory.Sequence(
        lambda number: (
            f"Тестовый факультет {number}"
        )
    )
    name_uz = factory.Sequence(
        lambda number: (
            f"Test fakulteti {number}"
        )
    )
    short_name_ru = factory.Sequence(
        lambda number: f"ТФ-{number}"
    )
    short_name_uz = factory.Sequence(
        lambda number: f"TF-{number}"
    )

    faculty_type = (
        Faculty.FacultyType.STANDARD
    )

    dean_name = ""
    phone = ""
    email = factory.Sequence(
        lambda number: (
            f"faculty{number}@example.com"
        )
    )

    is_active = True
    sort_order = 0

    created_by = factory.SelfAttribute(
        "university.created_by"
    )
    updated_by = factory.SelfAttribute(
        "university.updated_by"
    )


class DepartmentFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = Department

    faculty = factory.SubFactory(
        FacultyFactory
    )

    code = factory.Sequence(
        lambda number: f"DEP-{number:04d}"
    )
    name_ru = factory.Sequence(
        lambda number: (
            f"Тестовая кафедра {number}"
        )
    )
    name_uz = factory.Sequence(
        lambda number: (
            f"Test kafedrasi {number}"
        )
    )
    short_name_ru = factory.Sequence(
        lambda number: f"ТК-{number}"
    )
    short_name_uz = factory.Sequence(
        lambda number: f"TK-{number}"
    )

    head_name = ""
    phone = ""
    email = factory.Sequence(
        lambda number: (
            f"department{number}@example.com"
        )
    )
    room = ""

    is_active = True
    sort_order = 0

    created_by = factory.SelfAttribute(
        "faculty.created_by"
    )
    updated_by = factory.SelfAttribute(
        "faculty.updated_by"
    )