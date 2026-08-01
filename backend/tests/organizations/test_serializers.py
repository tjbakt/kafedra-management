from types import SimpleNamespace

from django.test import TestCase

from apps.organizations.api.serializers import (
    DepartmentSerializer,
    FacultySerializer,
    FacultyShortSerializer,
    UniversitySerializer,
)
from tests.factories import (
    DepartmentFactory,
    FacultyFactory,
    UniversityFactory,
    UserFactory,
)


class SerializerRequestMixin:
    def build_request(
        self,
        *,
        language="ru",
    ):
        user = UserFactory(
            interface_language=language,
        )

        return SimpleNamespace(
            user=user,
        )


class UniversitySerializerTests(
    SerializerRequestMixin,
    TestCase,
):
    def test_code_is_trimmed_and_uppercased(self):
        serializer = UniversitySerializer(
            data={
                "code": "  uni-test  ",
                "name_ru": "Университет",
                "name_uz": "Universitet",
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )
        self.assertEqual(
            serializer.validated_data["code"],
            "UNI-TEST",
        )

    def test_names_are_trimmed(self):
        serializer = UniversitySerializer(
            data={
                "code": "UNI-TRIM",
                "name_ru": "  Университет  ",
                "name_uz": "  Universitet  ",
                "short_name_ru": "  ТУ  ",
                "short_name_uz": "  TU  ",
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        self.assertEqual(
            serializer.validated_data["name_ru"],
            "Университет",
        )
        self.assertEqual(
            serializer.validated_data["name_uz"],
            "Universitet",
        )
        self.assertEqual(
            serializer.validated_data[
                "short_name_ru"
            ],
            "ТУ",
        )

    def test_display_name_uses_russian_language(self):
        university = UniversityFactory(
            name_ru="Русское название",
            name_uz="O‘zbekcha nom",
        )

        serializer = UniversitySerializer(
            university,
            context={
                "request": self.build_request(
                    language="ru",
                )
            },
        )

        self.assertEqual(
            serializer.data["display_name"],
            "Русское название",
        )

    def test_display_name_uses_uzbek_language(self):
        university = UniversityFactory(
            name_ru="Русское название",
            name_uz="O‘zbekcha nom",
        )

        serializer = UniversitySerializer(
            university,
            context={
                "request": self.build_request(
                    language="uz",
                )
            },
        )

        self.assertEqual(
            serializer.data["display_name"],
            "O‘zbekcha nom",
        )

    def test_display_short_name_falls_back_to_name(self):
        university = UniversityFactory(
            short_name_ru="",
            short_name_uz="",
            name_ru="Полное название",
        )

        serializer = UniversitySerializer(
            university,
            context={
                "request": self.build_request(
                    language="ru",
                )
            },
        )

        self.assertEqual(
            serializer.data[
                "display_short_name"
            ],
            "Полное название",
        )

    def test_archive_fields_are_read_only(self):
        university = UniversityFactory()

        serializer = UniversitySerializer(
            university,
            data={
                "is_archived": True,
                "name_ru": "Новое название",
            },
            partial=True,
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        instance = serializer.save()

        self.assertFalse(
            instance.is_archived
        )
        self.assertEqual(
            instance.name_ru,
            "Новое название",
        )


class FacultySerializerTests(TestCase):
    def valid_data(
        self,
        *,
        university,
    ):
        return {
            "university": university.pk,
            "faculty_type": "standard",
            "code": "FAC-SERIALIZER",
            "name_ru": "Факультет",
            "name_uz": "Fakultet",
        }

    def test_accepts_active_university(self):
        university = UniversityFactory(
            is_active=True,
        )

        serializer = FacultySerializer(
            data=self.valid_data(
                university=university,
            )
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_rejects_archived_university(self):
        university = UniversityFactory()
        university.archive()

        serializer = FacultySerializer(
            data=self.valid_data(
                university=university,
            )
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "university",
            serializer.errors,
        )

    def test_rejects_inactive_university(self):
        university = UniversityFactory(
            is_active=False,
        )

        serializer = FacultySerializer(
            data=self.valid_data(
                university=university,
            )
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "university",
            serializer.errors,
        )

    def test_contains_related_names_and_count(self):
        faculty = FacultyFactory()
        DepartmentFactory.create_batch(
            2,
            faculty=faculty,
        )

        faculty.departments_count = 2

        serializer = FacultySerializer(
            faculty
        )

        self.assertEqual(
            serializer.data["university_name"],
            faculty.university.name_ru,
        )
        self.assertEqual(
            serializer.data["departments_count"],
            2,
        )


class DepartmentSerializerTests(TestCase):
    def valid_data(
        self,
        *,
        faculty,
    ):
        return {
            "faculty": faculty.pk,
            "code": "DEP-SERIALIZER",
            "name_ru": "Кафедра",
            "name_uz": "Kafedra",
        }

    def test_accepts_active_faculty(self):
        faculty = FacultyFactory(
            is_active=True,
        )

        serializer = DepartmentSerializer(
            data=self.valid_data(
                faculty=faculty,
            )
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_rejects_archived_faculty(self):
        faculty = FacultyFactory()
        faculty.archive()

        serializer = DepartmentSerializer(
            data=self.valid_data(
                faculty=faculty,
            )
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "faculty",
            serializer.errors,
        )

    def test_rejects_inactive_faculty(self):
        faculty = FacultyFactory(
            is_active=False,
        )

        serializer = DepartmentSerializer(
            data=self.valid_data(
                faculty=faculty,
            )
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "faculty",
            serializer.errors,
        )

    def test_rejects_faculty_of_archived_university(
        self,
    ):
        university = UniversityFactory()
        faculty = FacultyFactory(
            university=university,
        )
        university.archive()

        serializer = DepartmentSerializer(
            data=self.valid_data(
                faculty=faculty,
            )
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "faculty",
            serializer.errors,
        )

    def test_contains_faculty_and_university_names(
        self,
    ):
        department = DepartmentFactory()

        serializer = DepartmentSerializer(
            department
        )

        self.assertEqual(
            serializer.data["faculty_name"],
            department.faculty.name_ru,
        )
        self.assertEqual(
            serializer.data["university"],
            department.faculty.university_id,
        )
        self.assertEqual(
            serializer.data["university_name"],
            (
                department.faculty
                .university.name_ru
            ),
        )

class FacultyShortSerializerTests(TestCase):
    def test_contains_display_name(self):
        faculty = FacultyFactory(
            name_ru="Факультет тестирования",
        )

        serializer = FacultyShortSerializer(
            faculty
        )

        self.assertEqual(
            serializer.data,
            {
                "id": faculty.pk,
                "code": faculty.code,
                "display_name": (
                    "Факультет тестирования"
                ),
            },
        )