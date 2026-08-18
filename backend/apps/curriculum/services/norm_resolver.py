from datetime import date

from apps.academics.models import (
    AcademicSemester,
    AcademicYear,
)

from apps.curriculum.models import (
    AcademicYearCreditNorm,
)


def resolve_academic_year_by_date(
    target_date: date,
) -> AcademicYear | None:
    """
    Определяет учебный год по календарной дате.

    В первую очередь используем реальные даты
    AcademicSemester.

    Например:
        02.09.2025
            -> осенний семестр 2025/2026
            -> AcademicYear 2025/2026

    Если семестры ещё не заведены, используем
    start_year/end_year учебного года.
    """

    semester = (
        AcademicSemester.objects
        .filter(
            start_date__lte=target_date,
            end_date__gte=target_date,
            is_archived=False,
        )
        .select_related(
            "academic_year",
        )
        .order_by(
            "start_date",
        )
        .first()
    )

    if semester:
        return semester.academic_year

    #
    # Fallback.
    #
    # Июль–декабрь:
    #   2025 -> 2025/2026
    #
    # Январь–июнь:
    #   2026 -> 2025/2026
    #
    if target_date.month >= 7:
        start_year = (
            target_date.year
        )

        return (
            AcademicYear.objects
            .filter(
                start_year=start_year,
                end_year=start_year + 1,
                is_archived=False,
            )
            .first()
        )

    return (
        AcademicYear.objects
        .filter(
            start_year=(
                target_date.year - 1
            ),
            end_year=(
                target_date.year
            ),
            is_archived=False,
        )
        .first()
    )


def resolve_curriculum_academic_year(
    curriculum,
) -> AcademicYear:
    """
    Определяет учебный год версии учебного плана.

    Приоритет:

    1. Дата утверждения.
    2. effective_academic_year.

    Для утверждённого 02.09.2025 плана
    получаем 2025/2026 независимо от ID
    записей в базе.
    """

    if curriculum.approved_at:
        academic_year = (
            resolve_academic_year_by_date(
                curriculum.approved_at,
            )
        )

        if academic_year:
            return academic_year

    return (
        curriculum
        .effective_academic_year
    )


def resolve_credit_norm(
    academic_year: AcademicYear,
) -> AcademicYearCreditNorm | None:
    """
    Возвращает норму кредита именно
    для указанного учебного года.

    Если точной записи нет, используем
    последнюю действовавшую норму.
    """

    exact = (
        AcademicYearCreditNorm.objects
        .filter(
            academic_year=academic_year,
            is_archived=False,
        )
        .select_related(
            "academic_year",
        )
        .first()
    )

    if exact:
        return exact

    return (
        AcademicYearCreditNorm.objects
        .filter(
            academic_year__start_year__lte=(
                academic_year.start_year
            ),
            is_archived=False,
        )
        .select_related(
            "academic_year",
        )
        .order_by(
            "-academic_year__start_year",
        )
        .first()
    )


def resolve_curriculum_credit_norm(
    curriculum,
) -> AcademicYearCreditNorm | None:
    """
    Норма кредита для учебного плана.
    """

    academic_year = (
        resolve_curriculum_academic_year(
            curriculum
        )
    )

    return resolve_credit_norm(
        academic_year
    )