from types import SimpleNamespace

from django.contrib.auth.models import (
    AnonymousUser,
)
from django.test import TestCase
from rest_framework.test import (
    APIRequestFactory,
)

from apps.access_control.models import (
    SystemRole,
)
from apps.access_control.permissions import (
    IsAcademicOffice,
    IsDepartmentHead,
    IsHROfficer,
    IsSystemAdministrator,
    IsTeacher,
    ReadOnlyOrAcademicManager,
)
from tests.factories import (
    UserFactory,
    UserRoleAssignmentFactory,
)


class PermissionTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = SimpleNamespace()

    def request(self, user, method="get"):
        request = getattr(
            self.factory,
            method,
        )("/test/")

        request.user = user

        return request

    def test_system_admin_permission(self):
        user = UserFactory()

        UserRoleAssignmentFactory.global_role(
            user=user,
            role_code=(
                SystemRole.Code.SYSTEM_ADMIN
            ),
        )

        self.assertTrue(
            IsSystemAdministrator()
            .has_permission(
                self.request(user),
                self.view,
            )
        )

    def test_system_admin_rejects_viewer(self):
        user = UserFactory()

        UserRoleAssignmentFactory.global_role(
            user=user,
            role_code=(
                SystemRole.Code.VIEWER
            ),
        )

        self.assertFalse(
            IsSystemAdministrator()
            .has_permission(
                self.request(user),
                self.view,
            )
        )

    def test_role_specific_permissions(self):
        test_cases = (
            (
                IsAcademicOffice,
                SystemRole.Code.ACADEMIC_OFFICE,
            ),
            (
                IsHROfficer,
                SystemRole.Code.HR_OFFICER,
            ),
            (
                IsDepartmentHead,
                SystemRole.Code.DEPARTMENT_HEAD,
            ),
            (
                IsTeacher,
                SystemRole.Code.TEACHER,
            ),
        )

        for permission_class, role_code in (
            test_cases
        ):
            with self.subTest(
                permission=(
                    permission_class.__name__
                )
            ):
                user = UserFactory()

                if (
                    role_code
                    == SystemRole.Code.DEPARTMENT_HEAD
                ):
                    (
                        UserRoleAssignmentFactory
                        .department_role(
                            user=user,
                        )
                    )
                elif (
                    role_code
                    == SystemRole.Code.TEACHER
                ):
                    (
                        UserRoleAssignmentFactory
                        .self_role(
                            user=user,
                        )
                    )
                else:
                    (
                        UserRoleAssignmentFactory
                        .global_role(
                            user=user,
                            role_code=role_code,
                        )
                    )

                self.assertTrue(
                    permission_class()
                    .has_permission(
                        self.request(user),
                        self.view,
                    )
                )

    def test_read_only_permission_allows_authenticated_get(
        self,
    ):
        user = UserFactory()

        self.assertTrue(
            ReadOnlyOrAcademicManager()
            .has_permission(
                self.request(user, "get"),
                self.view,
            )
        )

    def test_read_only_permission_rejects_anonymous(
        self,
    ):
        self.assertFalse(
            ReadOnlyOrAcademicManager()
            .has_permission(
                self.request(
                    AnonymousUser(),
                    "get",
                ),
                self.view,
            )
        )

    def test_write_requires_academic_manager(
        self,
    ):
        viewer = UserFactory()

        self.assertFalse(
            ReadOnlyOrAcademicManager()
            .has_permission(
                self.request(viewer, "post"),
                self.view,
            )
        )

        academic_user = UserFactory()

        UserRoleAssignmentFactory.global_role(
            user=academic_user,
            role_code=(
                SystemRole.Code.ACADEMIC_OFFICE
            ),
        )

        self.assertTrue(
            ReadOnlyOrAcademicManager()
            .has_permission(
                self.request(
                    academic_user,
                    "post",
                ),
                self.view,
            )
        )