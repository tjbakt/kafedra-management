from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.organizations.models import (
    Department,
    Faculty,
    University,
)
from tests.factories import (
    DepartmentFactory,
    FacultyFactory,
    UniversityFactory,
    UserFactory,
)


class UniversityModelTests(TestCase):
    def test_string_representation(self):
        university = UniversityFactory(
            name_ru="Тестовый университет",
        )

        self.assertEqual(
            str(university),
            "Тестовый университет",
        )

    def test_default_manager_hides_archived_object(self):
        university = UniversityFactory()
        university.archive()

        self.assertFalse(
            University.objects.filter(
                pk=university.pk,
            ).exists()
        )
        self.assertTrue(
            University.all_objects.filter(
                pk=university.pk,
                is_archived=True,
            ).exists()
        )

    def test_archive_stores_user_and_timestamp(self):
        user = UserFactory()
        university = UniversityFactory()

        university.archive(user=user)
        university.refresh_from_db()

        self.assertTrue(
            university.is_archived
        )
        self.assertEqual(
            university.archived_by,
            user,
        )
        self.assertIsNotNone(
            university.archived_at
        )

    def test_restore_clears_archive_fields(self):
        archive_user = UserFactory()
        restore_user = UserFactory()
        university = UniversityFactory()

        university.archive(user=archive_user)
        university.restore(user=restore_user)
        university.refresh_from_db()

        self.assertFalse(
            university.is_archived
        )
        self.assertIsNone(
            university.archived_at
        )
        self.assertIsNone(
            university.archived_by
        )
        self.assertEqual(
            university.updated_by,
            restore_user,
        )

    def test_delete_performs_soft_delete(self):
        university = UniversityFactory()
        university_id = university.pk

        university.delete()

        self.assertTrue(
            University.all_objects.filter(
                pk=university_id,
                is_archived=True,
            ).exists()
        )

    def test_all_objects_manager_exposes_archived(
            self,
    ):
        active = UniversityFactory()
        archived = UniversityFactory()
        archived.archive()

        archived_ids = set(
            University.all_objects
            .archived()
            .values_list(
                "id",
                flat=True,
            )
        )

        self.assertIn(
            archived.pk,
            archived_ids,
        )
        self.assertNotIn(
            active.pk,
            archived_ids,
        )

    def test_all_objects_manager_exposes_active(
            self,
    ):
        active = UniversityFactory()
        archived = UniversityFactory()
        archived.archive()

        active_ids = set(
            University.all_objects
            .active()
            .values_list(
                "id",
                flat=True,
            )
        )

        self.assertIn(
            active.pk,
            active_ids,
        )
        self.assertNotIn(
            archived.pk,
            active_ids,
        )

class FacultyModelTests(TestCase):
    def test_string_representation(self):
        faculty = FacultyFactory(
            name_ru="Факультет информатики",
        )

        self.assertEqual(
            str(faculty),
            "Факультет информатики",
        )

    def test_standard_type_is_supported(self):
        faculty = FacultyFactory(
            faculty_type=(
                Faculty.FacultyType.STANDARD
            ),
        )

        self.assertEqual(
            faculty.faculty_type,
            Faculty.FacultyType.STANDARD,
        )

    def test_magistracy_type_is_supported(self):
        faculty = FacultyFactory(
            faculty_type=(
                Faculty.FacultyType.MAGISTRACY
            ),
        )

        self.assertEqual(
            faculty.faculty_type,
            Faculty.FacultyType.MAGISTRACY,
        )


class DepartmentModelTests(TestCase):
    def test_string_representation(self):
        department = DepartmentFactory(
            name_ru="Кафедра программирования",
        )

        self.assertEqual(
            str(department),
            "Кафедра программирования",
        )

    def test_clean_rejects_archived_faculty(self):
        faculty = FacultyFactory()
        faculty.archive()

        department = DepartmentFactory.build(
            faculty=faculty,
        )

        with self.assertRaises(
            ValidationError
        ) as context:
            department.full_clean()

        self.assertIn(
            "faculty",
            context.exception.message_dict,
        )

    def test_clean_accepts_active_faculty(self):
        faculty = FacultyFactory(
            is_active=True,
        )
        department = DepartmentFactory.build(
            faculty=faculty,
        )

        department.full_clean()