from datetime import date
from decimal import Decimal

import factory

from apps.staff.models import (
    AcademicDegree,
    AcademicTitle,
    StaffEmployment,
    StaffEmploymentAcademicYear,
    StaffMember,
    StaffPosition,
    WorkloadNorm,
)
from tests.factories.accounts import UserFactory
from tests.factories.organizations import (
    DepartmentFactory,
)


class StaffPositionFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = StaffPosition

    code = factory.Sequence(
        lambda number: f"POSITION-{number:04d}"
    )
    name_ru = factory.Sequence(
        lambda number: f"Должность {number}"
    )
    name_uz = factory.Sequence(
        lambda number: f"Lavozim {number}"
    )

    category = StaffPosition.Category.TEACHING
    is_teaching_position = True
    is_active = True
    sort_order = 0

    created_by = factory.SubFactory(
        UserFactory
    )
    updated_by = factory.SelfAttribute(
        "created_by"
    )


class AcademicDegreeFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = AcademicDegree

    code = factory.Sequence(
        lambda number: f"DEGREE-{number:04d}"
    )
    name_ru = factory.Sequence(
        lambda number: f"Учёная степень {number}"
    )
    name_uz = factory.Sequence(
        lambda number: f"Ilmiy daraja {number}"
    )
    short_name_ru = factory.Sequence(
        lambda number: f"УС-{number}"
    )
    short_name_uz = factory.Sequence(
        lambda number: f"ID-{number}"
    )

    is_active = True
    sort_order = 0

    created_by = factory.SubFactory(
        UserFactory
    )
    updated_by = factory.SelfAttribute(
        "created_by"
    )


class AcademicTitleFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = AcademicTitle

    code = factory.Sequence(
        lambda number: f"TITLE-{number:04d}"
    )
    name_ru = factory.Sequence(
        lambda number: f"Учёное звание {number}"
    )
    name_uz = factory.Sequence(
        lambda number: f"Ilmiy unvon {number}"
    )
    short_name_ru = factory.Sequence(
        lambda number: f"УЗ-{number}"
    )
    short_name_uz = factory.Sequence(
        lambda number: f"IU-{number}"
    )

    is_active = True
    sort_order = 0

    created_by = factory.SubFactory(
        UserFactory
    )
    updated_by = factory.SelfAttribute(
        "created_by"
    )


class StaffMemberFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = StaffMember

    user = factory.SubFactory(
        UserFactory
    )

    personnel_number = factory.Sequence(
        lambda number: f"STAFF-{number:06d}"
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


class StaffEmploymentFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = StaffEmployment

    staff_member = factory.SubFactory(
        StaffMemberFactory
    )
    department = factory.SubFactory(
        DepartmentFactory
    )
    position = factory.SubFactory(
        StaffPositionFactory
    )

    employment_type = (
        StaffEmployment.EmploymentType.PRIMARY
    )
    rate = Decimal("1.00")
    start_date = date(2020, 9, 1)
    end_date = None

    is_primary = False
    is_active = True

    document_number = ""
    document_date = None
    notes = ""

    created_by = factory.SelfAttribute(
        "staff_member.created_by"
    )
    updated_by = factory.SelfAttribute(
        "staff_member.updated_by"
    )

    @classmethod
    def primary(
        cls,
        **kwargs,
    ):
        return cls(
            is_primary=True,
            employment_type=(
                StaffEmployment
                .EmploymentType
                .PRIMARY
            ),
            **kwargs,
        )


class StaffEmploymentAcademicYearFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = StaffEmploymentAcademicYear

    staff_employment = factory.SubFactory(
        StaffEmploymentFactory
    )

    academic_year = factory.SubFactory(
        "tests.factories.academics."
        "AcademicYearFactory"
    )

    rate = factory.LazyAttribute(
        lambda obj: obj.staff_employment.rate
    )

    academic_degree = factory.LazyAttribute(
        lambda obj: (
            obj.staff_employment
            .staff_member
            .academic_degree
        )
    )
    academic_title = factory.LazyAttribute(
        lambda obj: (
            obj.staff_employment
            .staff_member
            .academic_title
        )
    )

    is_active = True
    notes = ""

    created_by = factory.SelfAttribute(
        "staff_employment.created_by"
    )
    updated_by = factory.SelfAttribute(
        "staff_employment.updated_by"
    )


class WorkloadNormFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = WorkloadNorm

    academic_year = factory.SubFactory(
        "tests.factories.academics."
        "AcademicYearFactory"
    )

    rate = Decimal("1.00")
    has_academic_degree = False
    has_academic_title = False
    annual_hours = Decimal("850.00")

    is_active = True
    notes = ""

    created_by = factory.SelfAttribute(
        "academic_year.created_by"
    )
    updated_by = factory.SelfAttribute(
        "academic_year.updated_by"
    )