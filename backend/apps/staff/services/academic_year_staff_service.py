from __future__ import annotations

from django.db import models, transaction

from apps.staff.models import (
    StaffEmployment,
    StaffEmploymentAcademicYear,
)


class AcademicYearStaffService:
    """
    Массовое создание кадровых состояний
    назначений на учебный год.
    """

    @staticmethod
    def get_eligible_employments(
        *,
        academic_year,
        department=None,
    ):
        """
        Возвращает назначения, которые пересекаются
        с выбранным учебным годом.
        """

        queryset = (
            StaffEmployment.objects
            .filter(
                is_archived=False,
                is_active=True,
                staff_member__is_archived=False,
                staff_member__is_active=True,
                position__is_teaching_position=True,
            )
            .select_related(
                "staff_member",
                "staff_member__academic_degree",
                "staff_member__academic_title",
                "department",
                "position",
            )
        )

        if department is not None:
            queryset = queryset.filter(
                department=department
            )

        # Назначение должно начаться не позднее
        # окончания выбранного учебного года.
        queryset = queryset.filter(
            start_date__year__lte=academic_year.end_year
        )

        # Назначение либо ещё не завершено,
        # либо завершено не раньше начала учебного года.
        queryset = queryset.filter(
            models.Q(end_date__isnull=True)
            | models.Q(
                end_date__year__gte=(
                    academic_year.start_year
                )
            )
        )

        return queryset.order_by(
            "staff_member__last_name",
            "staff_member__first_name",
            "department__name_ru",
        )

    @classmethod
    @transaction.atomic
    def create_missing_records(
        cls,
        *,
        academic_year,
        department=None,
        created_by=None,
    ) -> dict:
        """
        Создаёт только отсутствующие годовые записи.

        Существующие записи не изменяются.
        Архивные записи не дублируются, а восстанавливаются.
        """

        employments = list(
            cls.get_eligible_employments(
                academic_year=academic_year,
                department=department,
            )
        )

        employment_ids = [
            employment.pk
            for employment in employments
        ]

        existing_records = {
            record.staff_employment_id: record
            for record in (
                StaffEmploymentAcademicYear
                .all_objects
                .filter(
                    staff_employment_id__in=(
                        employment_ids
                    ),
                    academic_year=academic_year,
                )
            )
        }

        records_to_create = []
        records_to_restore = []

        skipped = 0

        for employment in employments:
            existing = existing_records.get(
                employment.pk
            )

            if existing is not None:
                if existing.is_archived:
                    existing.is_archived = False
                    existing.archived_at = None
                    existing.archived_by = None
                    existing.is_active = True
                    existing.updated_by = created_by
                    records_to_restore.append(existing)
                else:
                    skipped += 1

                continue

            records_to_create.append(
                StaffEmploymentAcademicYear(
                    staff_employment=employment,
                    academic_year=academic_year,
                    rate=employment.rate,
                    academic_degree=(
                        employment
                        .staff_member
                        .academic_degree
                    ),
                    academic_title=(
                        employment
                        .staff_member
                        .academic_title
                    ),
                    is_active=True,
                    created_by=created_by,
                    updated_by=created_by,
                )
            )

        created_records = (
            StaffEmploymentAcademicYear.objects
            .bulk_create(
                records_to_create,
                batch_size=500,
            )
        )

        if records_to_restore:
            StaffEmploymentAcademicYear.all_objects.bulk_update(
                records_to_restore,
                fields=(
                    "is_archived",
                    "archived_at",
                    "archived_by",
                    "is_active",
                    "updated_by",
                ),
                batch_size=500,
            )

        return {
            "total_employments": len(employments),
            "created": len(created_records),
            "restored": len(records_to_restore),
            "skipped": skipped,
        }

    @classmethod
    def get_missing_employments(
        cls,
        *,
        academic_year,
        department=None,
    ):
        """
        Возвращает назначения, у которых отсутствует
        неархивная запись выбранного учебного года.
        """

        queryset = cls.get_eligible_employments(
            academic_year=academic_year,
            department=department,
        )

        return queryset.exclude(
            academic_year_records__academic_year=(
                academic_year
            ),
            academic_year_records__is_archived=False,
        )