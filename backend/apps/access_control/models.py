from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import BaseModel
from apps.organizations.models import Department, Faculty, University
from apps.staff.models import StaffMember


class SystemRole(BaseModel):
    """
    Справочник системных ролей.

    Роли создаются как справочные записи, чтобы позднее
    можно было добавлять новые роли без изменения модели User.
    """

    class Code(models.TextChoices):
        SYSTEM_ADMIN = (
            "system_admin",
            _("Администратор системы"),
        )
        ACADEMIC_OFFICE = (
            "academic_office",
            _("Учебный отдел"),
        )
        HR_OFFICER = (
            "hr_officer",
            _("Кадровая служба"),
        )
        DEAN_OFFICE = (
            "dean_office",
            _("Деканат"),
        )
        DEPARTMENT_HEAD = (
            "department_head",
            _("Заведующий кафедрой"),
        )
        TEACHER = (
            "teacher",
            _("Преподаватель"),
        )
        VIEWER = (
            "viewer",
            _("Наблюдатель"),
        )

    code = models.CharField(
        _("Код"),
        max_length=50,
        choices=Code.choices,
        unique=True,
        db_index=True,
    )
    name_ru = models.CharField(
        _("Название на русском"),
        max_length=255,
    )
    name_uz = models.CharField(
        _("Название на узбекском"),
        max_length=255,
    )
    description = models.TextField(
        _("Описание"),
        blank=True,
    )
    is_active = models.BooleanField(
        _("Активна"),
        default=True,
        db_index=True,
    )
    sort_order = models.PositiveIntegerField(
        _("Порядок сортировки"),
        default=0,
    )

    class Meta:
        verbose_name = _("Системная роль")
        verbose_name_plural = _("Системные роли")
        ordering = ("sort_order", "name_ru")

    def __str__(self):
        return self.name_ru

class UserRoleAssignment(BaseModel):
    """
    Назначение роли пользователю с ограничением области действия.

    Область может быть:
    - глобальной;
    - университетской;
    - факультетской;
    - кафедральной;
    - персональной.
    """

    class ScopeType(models.TextChoices):
        GLOBAL = "global", _("Вся система")
        UNIVERSITY = "university", _("Университет")
        FACULTY = "faculty", _("Факультет")
        DEPARTMENT = "department", _("Кафедра")
        SELF = "self", _("Только собственные данные")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Пользователь"),
        related_name="role_assignments",
        on_delete=models.CASCADE,
    )
    role = models.ForeignKey(
        SystemRole,
        verbose_name=_("Роль"),
        related_name="user_assignments",
        on_delete=models.PROTECT,
    )
    scope_type = models.CharField(
        _("Область действия"),
        max_length=20,
        choices=ScopeType.choices,
        default=ScopeType.SELF,
        db_index=True,
    )
    university = models.ForeignKey(
        University,
        verbose_name=_("Университет"),
        related_name="role_assignments",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    faculty = models.ForeignKey(
        Faculty,
        verbose_name=_("Факультет"),
        related_name="role_assignments",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    department = models.ForeignKey(
        Department,
        verbose_name=_("Кафедра"),
        related_name="role_assignments",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    staff_member = models.ForeignKey(
        StaffMember,
        verbose_name=_("Сотрудник"),
        related_name="role_assignments",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text=_(
            "Используется для персональной роли преподавателя."
        ),
    )
    valid_from = models.DateField(
        _("Действует с"),
        default=timezone.localdate,
    )
    valid_until = models.DateField(
        _("Действует до"),
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(
        _("Активно"),
        default=True,
        db_index=True,
    )
    notes = models.TextField(
        _("Примечание"),
        blank=True,
    )

    class Meta:
        verbose_name = _("Назначение роли")
        verbose_name_plural = _("Назначения ролей")
        ordering = (
            "user",
            "role__sort_order",
            "scope_type",
        )
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "user",
                    "role",
                    "scope_type",
                    "university",
                    "faculty",
                    "department",
                    "staff_member",
                ),
                condition=Q(
                    is_archived=False,
                    is_active=True,
                ),
                name="unique_active_user_role_scope",
            ),
        ]

    @property
    def is_current(self):
        today = timezone.localdate()

        if not self.is_active or self.is_archived:
            return False

        if self.valid_from and self.valid_from > today:
            return False

        if self.valid_until and self.valid_until < today:
            return False

        return True

    def clean(self):
        super().clean()

        if (
            self.valid_until
            and self.valid_from
            and self.valid_until < self.valid_from
        ):
            raise ValidationError(
                {
                    "valid_until": _(
                        "Дата окончания не может быть раньше "
                        "даты начала."
                    )
                }
            )

        scope_fields = {
            self.ScopeType.GLOBAL: (),
            self.ScopeType.UNIVERSITY: ("university",),
            self.ScopeType.FACULTY: ("faculty",),
            self.ScopeType.DEPARTMENT: ("department",),
            self.ScopeType.SELF: ("staff_member",),
        }

        required_fields = scope_fields[self.scope_type]

        for field_name in required_fields:
            if not getattr(self, f"{field_name}_id"):
                raise ValidationError(
                    {
                        field_name: _(
                            "Поле обязательно для выбранной "
                            "области действия."
                        )
                    }
                )

        if (
            self.scope_type == self.ScopeType.GLOBAL
            and any(
                (
                    self.university_id,
                    self.faculty_id,
                    self.department_id,
                    self.staff_member_id,
                )
            )
        ):
            raise ValidationError(
                {
                    "scope_type": _(
                        "Для глобальной роли нельзя указывать "
                        "организационную область."
                    )
                }
            )

        if self.faculty_id and self.university_id:
            if self.faculty.university_id != self.university_id:
                raise ValidationError(
                    {
                        "faculty": _(
                            "Факультет не относится к выбранному "
                            "университету."
                        )
                    }
                )

        if self.department_id and self.faculty_id:
            if self.department.faculty_id != self.faculty_id:
                raise ValidationError(
                    {
                        "department": _(
                            "Кафедра не относится к выбранному "
                            "факультету."
                        )
                    }
                )

        if self.department_id and self.university_id:
            department_university_id = (
                self.department.faculty.university_id
            )

            if department_university_id != self.university_id:
                raise ValidationError(
                    {
                        "department": _(
                            "Кафедра не относится к выбранному "
                            "университету."
                        )
                    }
                )

        if (
            self.role_id
            and self.role.code == SystemRole.Code.TEACHER
            and self.scope_type != self.ScopeType.SELF
        ):
            raise ValidationError(
                {
                    "scope_type": _(
                        "Роль преподавателя должна иметь область "
                        "«Только собственные данные»."
                    )
                }
            )

        if (
            self.role_id
            and self.role.code
            == SystemRole.Code.DEPARTMENT_HEAD
            and self.scope_type != self.ScopeType.DEPARTMENT
        ):
            raise ValidationError(
                {
                    "scope_type": _(
                        "Роль заведующего кафедрой должна быть "
                        "ограничена кафедрой."
                    )
                }
            )

    def __str__(self):
        return f"{self.user} — {self.role}"