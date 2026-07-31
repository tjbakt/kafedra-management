import factory
from django.utils import timezone

from apps.access_control.models import (
    SystemRole,
    UserRoleAssignment,
)

from tests.factories.accounts import (
    UserFactory,
)
from tests.factories.organizations import (
    DepartmentFactory,
    FacultyFactory,
    UniversityFactory,
)


ROLE_NAMES = {
    SystemRole.Code.SYSTEM_ADMIN: (
        "Администратор системы",
        "Tizim administratori",
    ),
    SystemRole.Code.ACADEMIC_OFFICE: (
        "Учебный отдел",
        "O‘quv bo‘limi",
    ),
    SystemRole.Code.HR_OFFICER: (
        "Кадровая служба",
        "Kadrlar bo‘limi",
    ),
    SystemRole.Code.DEAN_OFFICE: (
        "Деканат",
        "Dekanat",
    ),
    SystemRole.Code.DEPARTMENT_HEAD: (
        "Заведующий кафедрой",
        "Kafedra mudiri",
    ),
    SystemRole.Code.TEACHER: (
        "Преподаватель",
        "O‘qituvchi",
    ),
    SystemRole.Code.VIEWER: (
        "Наблюдатель",
        "Kuzatuvchi",
    ),
}


class SystemRoleFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = SystemRole
        django_get_or_create = (
            "code",
        )

    code = SystemRole.Code.VIEWER

    name_ru = factory.LazyAttribute(
        lambda obj: ROLE_NAMES[
            obj.code
        ][0]
    )
    name_uz = factory.LazyAttribute(
        lambda obj: ROLE_NAMES[
            obj.code
        ][1]
    )

    description = ""
    is_active = True
    sort_order = 0

    created_by = factory.SubFactory(
        UserFactory
    )
    updated_by = factory.SelfAttribute(
        "created_by"
    )


class UserRoleAssignmentFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = UserRoleAssignment

    user = factory.SubFactory(
        UserFactory
    )
    role = factory.SubFactory(
        SystemRoleFactory
    )

    scope_type = (
        UserRoleAssignment.ScopeType.GLOBAL
    )

    university = None
    faculty = None
    department = None
    staff_member = None

    valid_from = factory.LazyFunction(
        timezone.localdate
    )
    valid_until = None
    is_active = True
    notes = ""

    created_by = factory.SelfAttribute(
        "user"
    )
    updated_by = factory.SelfAttribute(
        "user"
    )

    @classmethod
    def global_role(
        cls,
        *,
        user=None,
        role_code=SystemRole.Code.SYSTEM_ADMIN,
        **kwargs,
    ):
        user = user or UserFactory()

        role = SystemRoleFactory(
            code=role_code,
            created_by=user,
            updated_by=user,
        )

        return cls(
            user=user,
            role=role,
            scope_type=(
                UserRoleAssignment
                .ScopeType
                .GLOBAL
            ),
            university=None,
            faculty=None,
            department=None,
            staff_member=None,
            created_by=user,
            updated_by=user,
            **kwargs,
        )

    @classmethod
    def university_role(
        cls,
        *,
        user=None,
        role_code=SystemRole.Code.VIEWER,
        university=None,
        **kwargs,
    ):
        user = user or UserFactory()

        university = (
            university
            or UniversityFactory(
                created_by=user,
                updated_by=user,
            )
        )

        role = SystemRoleFactory(
            code=role_code,
            created_by=user,
            updated_by=user,
        )

        return cls(
            user=user,
            role=role,
            scope_type=(
                UserRoleAssignment
                .ScopeType
                .UNIVERSITY
            ),
            university=university,
            faculty=None,
            department=None,
            staff_member=None,
            created_by=user,
            updated_by=user,
            **kwargs,
        )

    @classmethod
    def faculty_role(
        cls,
        *,
        user=None,
        role_code=SystemRole.Code.DEAN_OFFICE,
        faculty=None,
        **kwargs,
    ):
        user = user or UserFactory()

        faculty = (
            faculty
            or FacultyFactory(
                created_by=user,
                updated_by=user,
                university__created_by=user,
                university__updated_by=user,
            )
        )

        role = SystemRoleFactory(
            code=role_code,
            created_by=user,
            updated_by=user,
        )

        return cls(
            user=user,
            role=role,
            scope_type=(
                UserRoleAssignment
                .ScopeType
                .FACULTY
            ),
            university=None,
            faculty=faculty,
            department=None,
            staff_member=None,
            created_by=user,
            updated_by=user,
            **kwargs,
        )

    @classmethod
    def department_role(
        cls,
        *,
        user=None,
        role_code=(
            SystemRole.Code.DEPARTMENT_HEAD
        ),
        department=None,
        **kwargs,
    ):
        user = user or UserFactory()

        if department is None:
            university = UniversityFactory(
                created_by=user,
                updated_by=user,
            )
            faculty = FacultyFactory(
                university=university,
                created_by=user,
                updated_by=user,
            )
            department = DepartmentFactory(
                faculty=faculty,
                created_by=user,
                updated_by=user,
            )

        role = SystemRoleFactory(
            code=role_code,
            created_by=user,
            updated_by=user,
        )

        return cls(
            user=user,
            role=role,
            scope_type=(
                UserRoleAssignment
                .ScopeType
                .DEPARTMENT
            ),
            university=None,
            faculty=None,
            department=department,
            staff_member=None,
            created_by=user,
            updated_by=user,
            **kwargs,
        )