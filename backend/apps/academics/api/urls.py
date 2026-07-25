from rest_framework.routers import DefaultRouter

from apps.academics.api.views import (
    AcademicSemesterViewSet,
    AcademicYearViewSet,
    EducationDurationViewSet,
    EducationLevelViewSet,
    StudentGroupViewSet,
    StudyFormViewSet,
    StudyProgramViewSet,
)


router = DefaultRouter()

router.register(
    "academic-years",
    AcademicYearViewSet,
    basename="academic-year",
)
router.register(
    "education-levels",
    EducationLevelViewSet,
    basename="education-level",
)
router.register(
    "study-forms",
    StudyFormViewSet,
    basename="study-form",
)
router.register(
    "education-durations",
    EducationDurationViewSet,
    basename="education-duration",
)
router.register(
    "semesters",
    AcademicSemesterViewSet,
    basename="academic-semester",
)
router.register(
    "study-programs",
    StudyProgramViewSet,
    basename="study-program",
)
router.register(
    "student-groups",
    StudentGroupViewSet,
    basename="student-group",
)

urlpatterns = router.urls