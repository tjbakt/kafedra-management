from django.db.models.signals import (
    pre_delete,
    pre_save,
)
from django.dispatch import receiver

from apps.academics.services.closed_academic_year_guard import (
    ClosedAcademicYearMutationGuard,
)
from apps.staff.models import (
    StaffEmploymentAcademicYear,
    WorkloadNorm,
)
from apps.teaching.models import (
    PlannedWorkload,
    TeachingStream,
    TeachingStreamGroup,
)
from apps.academics.models import (
    AcademicSemester,
)
from apps.curriculum.models import (
    Curriculum,
    CurriculumDiscipline,
    CurriculumWorkload,
)


PROTECTED_MODELS = (
    AcademicSemester,
    Curriculum,
    CurriculumDiscipline,
    CurriculumWorkload,
    TeachingStream,
    TeachingStreamGroup,
    PlannedWorkload,
    StaffEmploymentAcademicYear,
    WorkloadNorm,
)


def get_previous_instance(instance):
    """
    Загружает состояние объекта до изменения.

    Используется для проверки старого academic_year,
    если пользователь пытается перенести запись
    из закрытого года в открытый.
    """

    if instance._state.adding or instance.pk is None:
        return None

    manager = getattr(
        instance.__class__,
        "all_objects",
        instance.__class__._default_manager,
    )

    return (
        manager
        .select_related(
            *select_related_fields(
                instance.__class__
            )
        )
        .filter(pk=instance.pk)
        .first()
    )


def select_related_fields(model_class):
    if model_class is AcademicSemester:
        return (
            "academic_year",
        )

    if model_class is Curriculum:
        return (
            "effective_academic_year",
        )

    if model_class is CurriculumDiscipline:
        return (
            "curriculum",
            (
                "curriculum__"
                "effective_academic_year"
            ),
        )

    if model_class is CurriculumWorkload:
        return (
            "curriculum_discipline",
            (
                "curriculum_discipline__"
                "curriculum"
            ),
            (
                "curriculum_discipline__"
                "curriculum__"
                "effective_academic_year"
            ),
        )

    if model_class is TeachingStream:
        return (
            "academic_year",
        )

    if model_class is TeachingStreamGroup:
        return (
            "teaching_stream",
            "teaching_stream__academic_year",
        )

    if model_class is PlannedWorkload:
        return (
            "academic_year",
        )

    if model_class is StaffEmploymentAcademicYear:
        return (
            "academic_year",
        )

    if model_class is WorkloadNorm:
        return (
            "academic_year",
        )

    return ()


@receiver(
    pre_save,
    sender=AcademicSemester,
)
@receiver(
    pre_save,
    sender=Curriculum,
)
@receiver(
    pre_save,
    sender=CurriculumDiscipline,
)
@receiver(
    pre_save,
    sender=CurriculumWorkload,
)
@receiver(
    pre_save,
    sender=TeachingStream,
)
@receiver(
    pre_save,
    sender=TeachingStreamGroup,
)
@receiver(
    pre_save,
    sender=PlannedWorkload,
)
@receiver(
    pre_save,
    sender=StaffEmploymentAcademicYear,
)
@receiver(
    pre_save,
    sender=WorkloadNorm,
)
def prevent_closed_year_save(
    sender,
    instance,
    raw=False,
    **kwargs,
):
    """
    Запрещает create/update/archive/restore объектов
    закрытого учебного года.
    """

    if raw:
        return

    previous_instance = get_previous_instance(
        instance
    )

    ClosedAcademicYearMutationGuard.ensure_instance_mutable(
        instance=instance,
        previous_instance=previous_instance,
    )


@receiver(
    pre_delete,
    sender=AcademicSemester,
)
@receiver(
    pre_delete,
    sender=Curriculum,
)
@receiver(
    pre_delete,
    sender=CurriculumDiscipline,
)
@receiver(
    pre_delete,
    sender=CurriculumWorkload,
)
@receiver(
    pre_delete,
    sender=TeachingStream,
)
@receiver(
    pre_delete,
    sender=TeachingStreamGroup,
)
@receiver(
    pre_delete,
    sender=PlannedWorkload,
)
@receiver(
    pre_delete,
    sender=StaffEmploymentAcademicYear,
)
@receiver(
    pre_delete,
    sender=WorkloadNorm,
)
def prevent_closed_year_delete(
    sender,
    instance,
    **kwargs,
):
    """
    Запрещает физическое удаление данных
    закрытого учебного года.
    """

    ClosedAcademicYearMutationGuard.ensure_instance_mutable(
        instance=instance,
    )