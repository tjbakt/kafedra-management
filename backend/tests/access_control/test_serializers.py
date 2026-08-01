from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.access_control.api.serializers import (
    SystemRoleSerializer,
    UserRoleAssignmentSerializer,
)
from apps.access_control.models import (
    SystemRole,
    UserRoleAssignment,
)
from tests.factories import (
    DepartmentFactory,
    FacultyFactory,
    StaffMemberFactory,
    SystemRoleFactory,
    UniversityFactory,
    UserFactory,
    UserRoleAssignmentFactory,
)


class SystemRoleSerializerTests(TestCase):
    def test_archive_fields_are_read_only(self):
        role = SystemRoleFactory()

        serializer = SystemRoleSerializer(
            role,
            data={
                "name_ru": "Новое название",
                "is_archived": True,
            },
            partial=True,
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        role = serializer.save()

        self.assertEqual(
            role.name_ru,
            "Новое название",
        )
        self.assertFalse(
            role.is_archived,
        )


class UserRoleAssignmentSerializerTests(
    TestCase
):
    def setUp(self):
        self.user = UserFactory()

        self.viewer_role = SystemRoleFactory(
            code=SystemRole.Code.VIEWER,
        )

    def base_data(self):
        return {
            "user": self.user.pk,
            "role": self.viewer_role.pk,
            "scope_type": (
                UserRoleAssignment
                .ScopeType
                .GLOBAL
            ),
            "valid_from": (
                timezone.localdate()
            ),
            "is_active": True,
            "notes": "",
        }

    def test_accepts_global_assignment(self):
        serializer = (
            UserRoleAssignmentSerializer(
                data=self.base_data()
            )
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_global_scope_rejects_department(
        self,
    ):
        data = self.base_data()
        data["department"] = (
            DepartmentFactory().pk
        )

        serializer = (
            UserRoleAssignmentSerializer(
                data=data
            )
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "scope_type",
            serializer.errors,
        )

    def test_department_scope_requires_department(
        self,
    ):
        data = self.base_data()
        data["scope_type"] = (
            UserRoleAssignment
            .ScopeType
            .DEPARTMENT
        )

        serializer = (
            UserRoleAssignmentSerializer(
                data=data
            )
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "department",
            serializer.errors,
        )

    def test_teacher_requires_self_scope(self):
        role = SystemRoleFactory(
            code=SystemRole.Code.TEACHER,
        )

        data = self.base_data()
        data["role"] = role.pk

        serializer = (
            UserRoleAssignmentSerializer(
                data=data
            )
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "scope_type",
            serializer.errors,
        )

    def test_teacher_requires_linked_staff_user(
        self,
    ):
        role = SystemRoleFactory(
            code=SystemRole.Code.TEACHER,
        )
        staff_member = StaffMemberFactory(
            user=None,
        )

        data = self.base_data()
        data.update(
            {
                "role": role.pk,
                "scope_type": (
                    UserRoleAssignment
                    .ScopeType
                    .SELF
                ),
                "staff_member": (
                    staff_member.pk
                ),
            }
        )

        serializer = (
            UserRoleAssignmentSerializer(
                data=data
            )
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "staff_member",
            serializer.errors,
        )

    def test_staff_member_must_match_user(self):
        role = SystemRoleFactory(
            code=SystemRole.Code.TEACHER,
        )
        other_user = UserFactory()
        staff_member = StaffMemberFactory(
            user=other_user,
        )

        data = self.base_data()
        data.update(
            {
                "role": role.pk,
                "scope_type": (
                    UserRoleAssignment
                    .ScopeType
                    .SELF
                ),
                "staff_member": (
                    staff_member.pk
                ),
            }
        )

        serializer = (
            UserRoleAssignmentSerializer(
                data=data
            )
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "staff_member",
            serializer.errors,
        )

    def test_valid_teacher_assignment(self):
        role = SystemRoleFactory(
            code=SystemRole.Code.TEACHER,
        )
        staff_member = StaffMemberFactory(
            user=self.user,
        )

        data = self.base_data()
        data.update(
            {
                "role": role.pk,
                "scope_type": (
                    UserRoleAssignment
                    .ScopeType
                    .SELF
                ),
                "staff_member": (
                    staff_member.pk
                ),
            }
        )

        serializer = (
            UserRoleAssignmentSerializer(
                data=data
            )
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_end_date_before_start_is_invalid(
        self,
    ):
        data = self.base_data()
        data["valid_until"] = (
            timezone.localdate()
            - timedelta(days=1)
        )

        serializer = (
            UserRoleAssignmentSerializer(
                data=data
            )
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "valid_until",
            serializer.errors,
        )

    def test_output_contains_related_names(self):
        assignment = (
            UserRoleAssignmentFactory
            .department_role(
                user=self.user,
            )
        )

        serializer = (
            UserRoleAssignmentSerializer(
                assignment
            )
        )

        self.assertEqual(
            serializer.data["username"],
            self.user.username,
        )
        self.assertEqual(
            serializer.data["role_code"],
            assignment.role.code,
        )
        self.assertEqual(
            serializer.data[
                "department_name"
            ],
            assignment.department.name_ru,
        )
        self.assertTrue(
            serializer.data["is_current"]
        )