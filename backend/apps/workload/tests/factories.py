from datetime import date
from decimal import Decimal
import uuid

from django.contrib.auth import get_user_model

from apps.academics.models import (
    AcademicSemester,
    AcademicYear,
    EducationLevel,
    StudyForm,
    StudyProgram,
)
from apps.curriculum.models import (
    Curriculum,
    CurriculumDiscipline,
    CurriculumWorkload,
    Discipline,
    WorkloadType,
)
from apps.organizations.models import Department, Faculty, University
from apps.staff.models import (
    StaffEmployment,
    StaffEmploymentAcademicYear,
    StaffMember,
    StaffPosition,
    WorkloadNorm,
)
from apps.teaching.models import PlannedWorkload, TeachingStream
from apps.workload.models import WorkloadDistribution

User = get_user_model()


def _uid(prefix: str = "x") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def create_user(**kwargs):
    defaults = {
        "username": _uid("user"),
        "email": f"{_uid('u')}@example.com",
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
        "start_year": start_year,
        "end_year": end_year,
        "is_active": True,
    }
    defaults.update(kwargs)
    return AcademicYear.objects.create(**defaults)


def create_academic_semester(*, academic_year=None, **kwargs):
    academic_year = academic_year or create_academic_year()
    defaults = {
        "academic_year": academic_year,
        "season": AcademicSemester.Season.AUTUMN,
        "start_date": date(academic_year.start_year, 9, 1),
        "end_date": date(academic_year.start_year, 12, 31),
        "is_active": True,
    }
    defaults.update(kwargs)
    return AcademicSemester.objects.create(**defaults)


def create_university(**kwargs):
    defaults = {
        "code": _uid("UNI"),
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
        "code": _uid("FAC"),
        "name_ru": "Тестовый факультет",
        "name_uz": "Test fakulteti",
        "is_active": True,
    }
    defaults.update(kwargs)
    return Faculty.objects.create(**defaults)


def create_department(*, faculty=None, **kwargs):
    faculty = faculty or create_faculty()
    uid = _uid("DEP")
    defaults = {
        "faculty": faculty,
        "code": uid,
        "name_ru": f"Тестовая кафедра {uid}",
        "name_uz": f"Test kafedrasi {uid}",
        "is_active": True,
    }
    defaults.update(kwargs)
    # если передали name_ru, но не name_uz — тоже сделаем уникальным
    if "name_ru" in kwargs and "name_uz" not in kwargs:
        defaults["name_uz"] = f"{kwargs['name_ru']} uz"
    return Department.objects.create(**defaults)


def create_position(**kwargs):
    defaults = {
        "code": _uid("POS"),
        "name_ru": "Доцент",
        "name_uz": "Dotsent",
        "is_teaching_position": True,
        "is_active": True,
    }
    defaults.update(kwargs)
    return StaffPosition.objects.create(**defaults)


def create_staff_member(**kwargs):
    defaults = {
        "personnel_number": _uid("T"),
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
    staff_member = staff_member or create_staff_member()
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


def create_year_staff_record(
    *,
    staff_employment=None,
    academic_year=None,
    rate=Decimal("1.00"),
    **kwargs,
):
    staff_employment = staff_employment or create_employment()
    academic_year = academic_year or create_academic_year()
    defaults = {
        "staff_employment": staff_employment,
        "academic_year": academic_year,
        "rate": rate,
        "is_active": True,
    }
    defaults.update(kwargs)
    return StaffEmploymentAcademicYear.objects.create(**defaults)


def create_workload_norm(
    *,
    academic_year=None,
    rate=Decimal("1.00"),
    has_academic_degree=False,
    has_academic_title=False,
    annual_hours=Decimal("600.00"),
    **kwargs,
):
    academic_year = academic_year or create_academic_year()
    defaults = {
        "academic_year": academic_year,
        "rate": rate,
        "has_academic_degree": has_academic_degree,
        "has_academic_title": has_academic_title,
        "annual_hours": annual_hours,
        "is_active": True,
    }
    defaults.update(kwargs)
    return WorkloadNorm.objects.create(**defaults)


def create_planned_workload(
    *,
    academic_year=None,
    academic_semester=None,
    department=None,
    total_hours=Decimal("100.00"),
    stream_code=None,
    **kwargs,
):
    """
    Минимальная цепочка объектов для PlannedWorkload.
    """
    academic_year = academic_year or create_academic_year()
    academic_semester = academic_semester or create_academic_semester(
        academic_year=academic_year,
    )
    department = department or create_department()

    education_level, _ = EducationLevel.objects.get_or_create(
        code=EducationLevel.Code.BACHELOR,
        defaults={
            "name_ru": "Бакалавриат",
            "name_uz": "Bakalavr",
            "is_active": True,
        },
    )
    study_form, _ = StudyForm.objects.get_or_create(
        code=StudyForm.Code.FULL_TIME,
        defaults={
            "name_ru": "Очная",
            "name_uz": "Kunduzgi",
            "is_active": True,
        },
    )
    study_program = StudyProgram.objects.create(
        university=department.faculty.university,
        education_level=education_level,
        code=_uid("SP"),
        name_ru="Тестовое направление",
        name_uz="Test yo'nalish",
        profiling_department=department,
        is_active=True,
    )
    curriculum = Curriculum.objects.create(
        study_program=study_program,
        study_form=study_form,
        effective_academic_year=academic_year,
        code=_uid("CUR"),
        is_active=True,
    )
    discipline = Discipline.objects.create(
        code=_uid("DISC"),
        name_ru="Тестовая дисциплина",
        name_uz="Test fan",
        is_active=True,
    )
    curriculum_discipline = CurriculumDiscipline.objects.create(
        curriculum=curriculum,
        discipline=discipline,
        semester_number=1,
        teaching_department=department,
        is_active=True,
    )
    workload_type, _ = WorkloadType.objects.get_or_create(
        code=WorkloadType.Code.LECTURE,
        defaults={
            "name_ru": "Лекции",
            "name_uz": "Ma'ruzalar",
            "calculation_mode": WorkloadType.CalculationMode.FIXED,
            "is_active": True,
        },
    )
    curriculum_workload = CurriculumWorkload.objects.create(
        curriculum_discipline=curriculum_discipline,
        workload_type=workload_type,
        calculation_mode=WorkloadType.CalculationMode.FIXED,
        base_hours=total_hours,
        is_active=True,
    )
    teaching_stream = TeachingStream.objects.create(
        academic_year=academic_year,
        academic_semester=academic_semester,
        curriculum_discipline=curriculum_discipline,
        curriculum_workload=curriculum_workload,
        teaching_department=department,
        code=stream_code or _uid("STR"),
        name="Тестовый поток",
        is_active=True,
    )

    defaults = {
        "teaching_stream": teaching_stream,
        "academic_year": academic_year,
        "academic_semester": academic_semester,
        "teaching_department": department,
        "curriculum_workload": curriculum_workload,
        "calculation_mode": WorkloadType.CalculationMode.FIXED,
        "base_hours": total_hours,
        "calculation_quantity": Decimal("1.00"),
        "total_hours": total_hours,
        "groups_count": 1,
        "subgroups_count": 1,
        "students_count": 25,
        "status": PlannedWorkload.Status.CALCULATED,
    }
    defaults.update(kwargs)
    return PlannedWorkload.objects.create(**defaults)


def create_distribution(
    *,
    planned_workload=None,
    staff_employment=None,
    allocated_hours=Decimal("20.00"),
    status=WorkloadDistribution.Status.DRAFT,
    user=None,
    **kwargs,
):
    planned_workload = planned_workload or create_planned_workload()
    staff_employment = staff_employment or create_employment(
        department=planned_workload.teaching_department,
    )
    defaults = {
        "planned_workload": planned_workload,
        "staff_employment": staff_employment,
        "allocated_hours": allocated_hours,
        "status": status,
        "created_by": user,
        "updated_by": user,
    }
    defaults.update(kwargs)
    return WorkloadDistribution.objects.create(**defaults)