from django.test import TestCase

from apps.organizations.models import (
    Department,
)
from tests.factories import (
    DepartmentFactory,
    UserFactory,
)


class ArchivableModelTests(TestCase):
    def test_active_manager_excludes_archived(
        self,
    ):
        active = DepartmentFactory()
        archived = DepartmentFactory()

        archived.archive()

        self.assertTrue(
            Department.objects.filter(
                pk=active.pk,
            ).exists()
        )
        self.assertFalse(
            Department.objects.filter(
                pk=archived.pk,
            ).exists()
        )

    def test_all_objects_contains_archived(
        self,
    ):
        department = DepartmentFactory()

        department.archive()

        self.assertTrue(
            Department.all_objects.filter(
                pk=department.pk,
            ).exists()
        )

    def test_archive_sets_fields(self):
        user = UserFactory()
        department = DepartmentFactory()

        department.archive(user=user)
        department.refresh_from_db()

        self.assertTrue(
            department.is_archived
        )
        self.assertIsNotNone(
            department.archived_at
        )
        self.assertEqual(
            department.archived_by,
            user,
        )

    def test_archive_is_idempotent(self):
        first_user = UserFactory()
        second_user = UserFactory()

        department = DepartmentFactory()

        department.archive(user=first_user)
        first_archived_at = (
            department.archived_at
        )

        department.archive(user=second_user)
        department.refresh_from_db()

        self.assertEqual(
            department.archived_at,
            first_archived_at,
        )
        self.assertEqual(
            department.archived_by,
            first_user,
        )

    def test_restore_clears_archive_fields(
        self,
    ):
        archive_user = UserFactory()
        restore_user = UserFactory()

        department = DepartmentFactory()

        department.archive(
            user=archive_user
        )
        department.restore(
            user=restore_user
        )
        department.refresh_from_db()

        self.assertFalse(
            department.is_archived
        )
        self.assertIsNone(
            department.archived_at
        )
        self.assertIsNone(
            department.archived_by
        )
        self.assertEqual(
            department.updated_by,
            restore_user,
        )

    def test_restore_is_idempotent(self):
        department = DepartmentFactory()

        original_updated_by = (
            department.updated_by
        )

        department.restore(
            user=UserFactory()
        )
        department.refresh_from_db()

        self.assertFalse(
            department.is_archived
        )
        self.assertEqual(
            department.updated_by,
            original_updated_by,
        )

    def test_delete_archives_instead_of_deleting(
        self,
    ):
        department = DepartmentFactory()
        department_id = department.pk

        department.delete()

        self.assertFalse(
            Department.objects.filter(
                pk=department_id,
            ).exists()
        )
        self.assertTrue(
            Department.all_objects.filter(
                pk=department_id,
                is_archived=True,
            ).exists()
        )

    def test_hard_delete_removes_record(self):
        department = DepartmentFactory()
        department_id = department.pk

        department.hard_delete()

        self.assertFalse(
            Department.all_objects.filter(
                pk=department_id,
            ).exists()
        )