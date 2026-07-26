from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model

from apps.academics.models import AcademicYear
from apps.organizations.models import (
    Department,
    Faculty,
    University,
)
from apps.staff.models import (
    AcademicDegree,
    AcademicTitle,
    StaffEmployment,
    StaffMember,
    StaffPosition,
)

User = get_user_model()


def create_user(**kwargs):
    defaults = {
        "username": "test-user",
        "email": "test@example.com",
    }
    defaults.update(kwargs)

    return User.objects.create_user(
        password="test-password",
        **defaults,
    )


def create_academic_year(
    *,
    start_year=2026,
    end_year=2027,
    **kwargs,
):
    defaults = {
        "name": f"{start_year}/{end_year}",
        "start_year": start_year,
        "end_year": end_year,
        "is_active": True,
    }
    defaults.update(kwargs)

    return AcademicYear.objects.create(**defaults)


def create_university(**kwargs):
    defaults = {
        "name_ru": "Тестовый университет",
        "name_uz": "Test universiteti",
        "is_active": True,
    }
    defaults.update(kwargs)

    return University.objects.create(**defaults)


def create_faculty(*, university=None, **kwargs):
    university = university or create_university()

    defaults = {
        "university": university,
        "name_ru": "Тестовый факультет",
        "name_uz": "Test fakulteti",
        "is_active": True,
    }
    defaults.update(kwargs)

    return Faculty.objects.create(**defaults)


def create_department(*, faculty=None, **kwargs):
    faculty = faculty or create_faculty()

    defaults = {
        "faculty": faculty,
        "name_ru": "Тестовая кафедра",
        "name_uz": "Test kafedrasi",
        "is_active": True,
    }
    defaults.update(kwargs)

    return Department.objects.create(**defaults)


def create_position(**kwargs):
    defaults = {
        "name_ru": "Доцент",
        "name_uz": "Dotsent",
        "is_teaching_position": True,
        "is_active": True,
    }
    defaults.update(kwargs)

    return StaffPosition.objects.create(**defaults)


def create_degree(**kwargs):
    defaults = {
        "name_ru": "Кандидат наук",
        "name_uz": "Fan nomzodi",
        "is_active": True,
    }
    defaults.update(kwargs)

    return AcademicDegree.objects.create(**defaults)


def create_title(**kwargs):
    defaults = {
        "name_ru": "Доцент",
        "name_uz": "Dotsent",
        "is_active": True,
    }
    defaults.update(kwargs)

    return AcademicTitle.objects.create(**defaults)


def create_staff_member(**kwargs):
    defaults = {
        "personnel_number": "T-001",
        "last_name": "Иванов",
        "first_name": "Иван",
        "middle_name": "Иванович",
        "is_active": True,
    }
    defaults.update(kwargs)

    return StaffMember.objects.create(**defaults)


def create_employment(
    *,
    staff_member=None,
    department=None,
    position=None,
    **kwargs,
):
    staff_member = (
        staff_member or create_staff_member()
    )
    department = department or create_department()
    position = position or create_position()

    defaults = {
        "staff_member": staff_member,
        "department": department,
        "position": position,
        "rate": Decimal("1.00"),
        "start_date": date(2025, 9, 1),
        "is_active": True,
    }
    defaults.update(kwargs)

    return StaffEmployment.objects.create(**defaults)