from apps.academics.models import (
    AcademicYear,
)

from apps.curriculum.models import (
    AcademicYearCreditNorm,
)


def resolve_credit_norm(
    academic_year: AcademicYear,
) -> AcademicYearCreditNorm | None:
    """
    Норма кредита действует начиная
    с года, для которого была установлена,
    пока не будет установлена новая.

    Например:
      2024/2025 = 30 часов

    Если для 2026/2027 отдельной записи
    нет, продолжает действовать 30 часов.
    """

    exact = (
        AcademicYearCreditNorm
        .objects
        .filter(
            academic_year=(
                academic_year
            ),
            is_archived=False,
        )
        .first()
    )

    if exact:
        return exact

    return (
        AcademicYearCreditNorm
        .objects
        .filter(
            academic_year__start_year__lte=(
                academic_year.start_year
            ),
            is_archived=False,
        )
        .select_related(
            "academic_year"
        )
        .order_by(
            "-academic_year__start_year"
        )
        .first()
    )