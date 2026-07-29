from django.utils.translation import get_language
from rest_framework import serializers

from apps.academics.models import (
    AcademicSemester,
    AcademicYear,
    EducationDuration,
    EducationLevel,
    StudentGroup,
    StudyForm,
    StudyProgram,
)
from apps.common.api.serializers import AuditFieldsSerializer
from apps.workload.api.serializers import (
    AcademicYearClosingReadinessResultSerializer,
)


class LocalizedNameMixin:
    display_name = serializers.SerializerMethodField()

    def get_display_name(self, obj):
        request = self.context.get("request")

        if (
            request
            and request.user
            and request.user.is_authenticated
        ):
            language = request.user.interface_language
        else:
            language = (get_language() or "ru")[:2]

        if language == "uz":
            return obj.name_uz or obj.name_ru

        return obj.name_ru or obj.name_uz


class AcademicYearSerializer(AuditFieldsSerializer):
    name = serializers.CharField(read_only=True)
    status_label = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )
    is_closed = serializers.BooleanField(
        read_only=True,
    )
    closed_by_name = serializers.SerializerMethodField()
    reopened_by_name = serializers.SerializerMethodField()

    class Meta:
        model = AcademicYear
        fields = (
            "id",
            "start_year",
            "end_year",
            "name",
            "is_current",
            "is_active",

            "status",
            "status_label",
            "is_closed",

            "closed_at",
            "closed_by",
            "closed_by_name",
            "closing_comment",

            "reopened_at",
            "reopened_by",
            "reopened_by_name",
            "reopening_reason",

            "created_at",
            "updated_at",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",

            "is_archived",
            "archived_at",
            "archived_by",
            "archived_by_name",
        )
        read_only_fields = (
            "id",
            "name",

            "status",
            "status_label",
            "is_closed",

            "closed_at",
            "closed_by",
            "closed_by_name",
            "closing_comment",

            "reopened_at",
            "reopened_by",
            "reopened_by_name",
            "reopening_reason",

            "created_at",
            "updated_at",
            "created_by",
            "updated_by",

            "is_archived",
            "archived_at",
            "archived_by",
        )

    def get_closed_by_name(self, obj):
        return self._user_name(
            obj.closed_by
        )

    def get_reopened_by_name(self, obj):
        return self._user_name(
            obj.reopened_by
        )

    @staticmethod
    def _user_name(user):
        if user is None:
            return None

        full_name = user.get_full_name().strip()

        return full_name or str(user)

    def validate(self, attrs):
        instance = getattr(self, "instance", None)
        if (
                instance is not None
                and instance.is_closed
        ):
            raise serializers.ValidationError(
                {
                    "academic_year": (
                        "Закрытый учебный год нельзя "
                        "изменять. Сначала повторно "
                        "откройте его."
                    )
                }
            )

        start_year = attrs.get(
            "start_year",
            getattr(instance, "start_year", None),
        )
        end_year = attrs.get(
            "end_year",
            getattr(instance, "end_year", None),
        )

        if (
            start_year is not None
            and end_year is not None
            and end_year != start_year + 1
        ):
            raise serializers.ValidationError(
                {
                    "end_year": (
                        "Год окончания должен следовать "
                        "за годом начала."
                    )
                }
            )

        return attrs

class CloseAcademicYearSerializer(
    serializers.Serializer
):
    comment = serializers.CharField(
        required=False,
        allow_blank=True,
        trim_whitespace=True,
        max_length=5000,
    )


class ReopenAcademicYearSerializer(
    serializers.Serializer
):
    reason = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
        max_length=5000,
    )

    def validate_reason(self, value):
        normalized = value.strip()

        if not normalized:
            raise serializers.ValidationError(
                (
                    "Для повторного открытия необходимо "
                    "указать причину."
                )
            )

        return normalized


class AcademicYearClosingOperationResultSerializer(
    serializers.Serializer
):
    id = serializers.IntegerField()
    name = serializers.CharField()

    status = serializers.ChoiceField(
        choices=AcademicYear.Status.choices,
    )
    status_label = serializers.CharField()

    is_current = serializers.BooleanField()
    is_active = serializers.BooleanField()

    closed_at = serializers.DateTimeField(
        allow_null=True,
    )
    closed_by = serializers.IntegerField(
        allow_null=True,
    )
    closed_by_name = serializers.CharField(
        allow_null=True,
        allow_blank=True,
    )
    closing_comment = serializers.CharField(
        allow_blank=True,
    )

    reopened_at = serializers.DateTimeField(
        allow_null=True,
    )
    reopened_by = serializers.IntegerField(
        allow_null=True,
    )
    reopened_by_name = serializers.CharField(
        allow_null=True,
        allow_blank=True,
    )
    reopening_reason = serializers.CharField(
        allow_blank=True,
    )

    readiness = (
        AcademicYearClosingReadinessResultSerializer(
            required=False,
        )
    )


class EducationLevelSerializer(
    LocalizedNameMixin,
    AuditFieldsSerializer,
):
    class Meta:
        model = EducationLevel
        fields = (
            "id",
            "code",
            "name_ru",
            "name_uz",
            "display_name",
            "is_active",
            "sort_order",
            "created_at",
            "updated_at",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "is_archived",
            "archived_at",
            "archived_by",
            "archived_by_name",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "is_archived",
            "archived_at",
            "archived_by",
        )


class StudyFormSerializer(
    LocalizedNameMixin,
    AuditFieldsSerializer,
):
    class Meta:
        model = StudyForm
        fields = (
            "id",
            "code",
            "name_ru",
            "name_uz",
            "display_name",
            "is_active",
            "sort_order",
            "created_at",
            "updated_at",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "is_archived",
            "archived_at",
            "archived_by",
            "archived_by_name",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "is_archived",
            "archived_at",
            "archived_by",
        )


class EducationDurationSerializer(AuditFieldsSerializer):
    education_level_name = serializers.CharField(
        source="education_level.name_ru",
        read_only=True,
    )
    study_form_name = serializers.CharField(
        source="study_form.name_ru",
        read_only=True,
    )

    class Meta:
        model = EducationDuration
        fields = (
            "id",
            "education_level",
            "education_level_name",
            "study_form",
            "study_form_name",
            "duration_months",
            "semesters_count",
            "is_active",
            "created_at",
            "updated_at",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "is_archived",
            "archived_at",
            "archived_by",
            "archived_by_name",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "is_archived",
            "archived_at",
            "archived_by",
        )

    def validate(self, attrs):
        instance = getattr(self, "instance", None)

        duration_months = attrs.get(
            "duration_months",
            getattr(instance, "duration_months", None),
        )
        semesters_count = attrs.get(
            "semesters_count",
            getattr(instance, "semesters_count", None),
        )

        if (
            duration_months
            and semesters_count
            and duration_months != semesters_count * 6
        ):
            raise serializers.ValidationError(
                {
                    "duration_months": (
                        "Продолжительность должна соответствовать "
                        "количеству семестров."
                    )
                }
            )

        return attrs


class AcademicSemesterSerializer(AuditFieldsSerializer):
    academic_year_name = serializers.CharField(
        source="academic_year.name",
        read_only=True,
    )
    season_name = serializers.CharField(
        source="get_season_display",
        read_only=True,
    )

    class Meta:
        model = AcademicSemester
        fields = (
            "id",
            "academic_year",
            "academic_year_name",
            "season",
            "season_name",
            "start_date",
            "end_date",
            "is_current",
            "is_active",
            "created_at",
            "updated_at",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "is_archived",
            "archived_at",
            "archived_by",
            "archived_by_name",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "is_archived",
            "archived_at",
            "archived_by",
        )


class StudyProgramSerializer(
    LocalizedNameMixin,
    AuditFieldsSerializer,
):
    university_name = serializers.CharField(
        source="university.name_ru",
        read_only=True,
    )
    education_level_name = serializers.CharField(
        source="education_level.name_ru",
        read_only=True,
    )
    profiling_department_name = serializers.CharField(
        source="profiling_department.name_ru",
        read_only=True,
    )
    profiling_faculty = serializers.IntegerField(
        source="profiling_department.faculty_id",
        read_only=True,
    )
    profiling_faculty_name = serializers.CharField(
        source="profiling_department.faculty.name_ru",
        read_only=True,
    )

    class Meta:
        model = StudyProgram
        fields = (
            "id",
            "university",
            "university_name",
            "education_level",
            "education_level_name",
            "code",
            "name_ru",
            "name_uz",
            "display_name",
            "profiling_department",
            "profiling_department_name",
            "profiling_faculty",
            "profiling_faculty_name",
            "is_active",
            "sort_order",
            "created_at",
            "updated_at",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "is_archived",
            "archived_at",
            "archived_by",
            "archived_by_name",
        )
        read_only_fields = (
            "id",
            "profiling_faculty",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "is_archived",
            "archived_at",
            "archived_by",
        )

    def validate_code(self, value):
        return value.strip().upper()

    def validate(self, attrs):
        instance = getattr(self, "instance", None)

        university = attrs.get(
            "university",
            getattr(instance, "university", None),
        )
        department = attrs.get(
            "profiling_department",
            getattr(instance, "profiling_department", None),
        )

        if university and department:
            if department.faculty.university_id != university.id:
                raise serializers.ValidationError(
                    {
                        "profiling_department": (
                            "Профилирующая кафедра должна относиться "
                            "к выбранному университету."
                        )
                    }
                )

            if department.is_archived or not department.is_active:
                raise serializers.ValidationError(
                    {
                        "profiling_department": (
                            "Выбранная кафедра недоступна."
                        )
                    }
                )

        return attrs


class StudentGroupSerializer(AuditFieldsSerializer):
    faculty_name = serializers.CharField(
        source="faculty.name_ru",
        read_only=True,
    )
    faculty_type = serializers.CharField(
        source="faculty.faculty_type",
        read_only=True,
    )
    study_program_name = serializers.CharField(
        source="study_program.name_ru",
        read_only=True,
    )
    education_level = serializers.IntegerField(
        source="study_program.education_level_id",
        read_only=True,
    )
    education_level_name = serializers.CharField(
        source="study_program.education_level.name_ru",
        read_only=True,
    )
    study_form_name = serializers.CharField(
        source="study_form.name_ru",
        read_only=True,
    )
    admission_academic_year_name = serializers.CharField(
        source="academic_year_admission.name",
        read_only=True,
    )
    graduation_academic_year_name = serializers.CharField(
        source="graduation_academic_year.name",
        read_only=True,
        allow_null=True,
    )
    profiling_department = serializers.IntegerField(
        source="study_program.profiling_department_id",
        read_only=True,
    )
    profiling_department_name = serializers.CharField(
        source="study_program.profiling_department.name_ru",
        read_only=True,
    )
    profiling_department_faculty = serializers.IntegerField(
        source="study_program.profiling_department.faculty_id",
        read_only=True,
    )
    profiling_department_faculty_name = serializers.CharField(
        source="study_program.profiling_department.faculty.name_ru",
        read_only=True,
    )

    class Meta:
        model = StudentGroup
        fields = (
            "id",
            "code",
            "academic_year_admission",
            "admission_academic_year_name",
            "graduation_academic_year",
            "graduation_academic_year_name",
            "faculty",
            "faculty_name",
            "faculty_type",
            "study_program",
            "study_program_name",
            "education_level",
            "education_level_name",
            "study_form",
            "study_form_name",
            "profiling_department",
            "profiling_department_name",
            "profiling_department_faculty",
            "profiling_department_faculty_name",
            "student_count",
            "subgroup_count",
            "is_active",
            "notes",
            "created_at",
            "updated_at",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "is_archived",
            "archived_at",
            "archived_by",
            "archived_by_name",
        )
        read_only_fields = (
            "id",
            "education_level",
            "profiling_department",
            "profiling_department_faculty",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "is_archived",
            "archived_at",
            "archived_by",
        )

    def validate_code(self, value):
        return value.strip().upper()

    def validate(self, attrs):
        instance = getattr(self, "instance", None)

        faculty = attrs.get(
            "faculty",
            getattr(instance, "faculty", None),
        )
        study_program = attrs.get(
            "study_program",
            getattr(instance, "study_program", None),
        )
        study_form = attrs.get(
            "study_form",
            getattr(instance, "study_form", None),
        )

        if faculty and study_program:
            if faculty.university_id != study_program.university_id:
                raise serializers.ValidationError(
                    {
                        "faculty": (
                            "Факультет группы и направление обучения "
                            "должны относиться к одному университету."
                        )
                    }
                )

        if study_program and study_form:
            duration_exists = EducationDuration.objects.filter(
                education_level=study_program.education_level,
                study_form=study_form,
                is_active=True,
            ).exists()

            if not duration_exists:
                raise serializers.ValidationError(
                    {
                        "study_form": (
                            "Для выбранной степени и формы обучения "
                            "не задана продолжительность."
                        )
                    }
                )

        return attrs