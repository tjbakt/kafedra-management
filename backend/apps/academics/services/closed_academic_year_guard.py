from django.core.exceptions import ValidationError, ObjectDoesNotExist

from apps.academics.exceptions import (
    AcademicYearClosingError,
)
from apps.academics.services.academic_year_closing_service import (
    AcademicYearClosingService,
)


class ClosedAcademicYearMutationGuard:
    """
    Единая защита связанных объектов закрытого
    учебного года.

    Проверяет как текущий учебный год объекта,
    так и новый учебный год при переносе записи.
    """

    ERROR_CODE = "academic_year_closed"

    @classmethod
    def ensure_open(
        cls,
        *,
        academic_year,
    ):
        if academic_year is None:
            return

        try:
            AcademicYearClosingService.ensure_open(
                academic_year=academic_year,
            )
        except AcademicYearClosingError as exc:
            raise cls._validation_error(
                academic_year=academic_year,
                source_exception=exc,
            ) from exc

    @classmethod
    def ensure_instance_mutable(
        cls,
        *,
        instance,
        previous_instance=None,
    ):
        """
        Проверяет учебные годы старого и нового
        состояния объекта.

        Это запрещает обход защиты путём замены
        academic_year закрытой записи.
        """

        previous_year = cls.resolve_academic_year(
            previous_instance
        )
        current_year = cls.resolve_academic_year(
            instance
        )

        checked_year_ids = set()

        for academic_year in (
            previous_year,
            current_year,
        ):
            if academic_year is None:
                continue

            identity = getattr(
                academic_year,
                "pk",
                None,
            )

            if identity in checked_year_ids:
                continue

            cls.ensure_open(
                academic_year=academic_year,
            )

            checked_year_ids.add(identity)

    @classmethod
    def resolve_academic_year(
        cls,
        instance,
    ):
        """
        Определяет AcademicYear для поддерживаемого
        объекта без привязки к конкретному приложению.
        """

        if instance is None:
            return None

        direct_year = cls._related_object(
            instance=instance,
            relation_name="academic_year",
        )
        if direct_year is not None:
            return direct_year

        teaching_stream = cls._related_object(
            instance=instance,
            relation_name="teaching_stream",
        )
        if teaching_stream is not None:
            return cls._related_object(
                instance=teaching_stream,
                relation_name="academic_year",
            )

        planned_workload = cls._related_object(
            instance=instance,
            relation_name="planned_workload",
        )
        if planned_workload is not None:
            return cls._related_object(
                instance=planned_workload,
                relation_name="academic_year",
            )

        group_semester = cls._related_object(
            instance=instance,
            relation_name="group_semester",
        )
        if group_semester is not None:
            return cls._related_object(
                instance=group_semester,
                relation_name="academic_year",
            )

        return None

    @staticmethod
    def _related_object(
        *,
        instance,
        relation_name,
    ):
        relation_id_name = f"{relation_name}_id"

        if not hasattr(
            instance,
            relation_id_name,
        ):
            return None

        if getattr(
            instance,
            relation_id_name,
            None,
        ) is None:
            return None

        try:
            return getattr(
                instance,
                relation_name,
            )
        except (
            AttributeError,
            ObjectDoesNotExist,
        ):
            return None

    @classmethod
    def _validation_error(
        cls,
        *,
        academic_year,
        source_exception,
    ):
        details = (
            source_exception.details or {}
        )

        closed_at = details.get("closed_at")

        if (
            closed_at is None
            and academic_year.closed_at
        ):
            closed_at = (
                academic_year
                .closed_at
                .isoformat()
            )

        return ValidationError(
            {
                "code": cls.ERROR_CODE,
                "detail": source_exception.message,
                "academic_year": (
                    details.get("academic_year")
                    or academic_year.pk
                ),
                "academic_year_name": (
                    details.get(
                        "academic_year_name"
                    )
                    or academic_year.name
                ),
                "closed_at": closed_at,
            }
        )