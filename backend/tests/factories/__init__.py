from tests.factories.accounts import (
    StaffUserFactory,
    SuperUserFactory,
    UserFactory,
)
from tests.factories.access_control import (
    SystemRoleFactory,
    UserRoleAssignmentFactory,
)
from tests.factories.academics import (
    AcademicSemesterFactory,
    AcademicYearFactory,
    EducationDurationFactory,
    EducationLevelFactory,
    StudentGroupFactory,
    StudyFormFactory,
    StudyProgramFactory,
)
from tests.factories.organizations import (
    DepartmentFactory,
    FacultyFactory,
    UniversityFactory,
)
from tests.factories.staff import (
    AcademicDegreeFactory,
    AcademicTitleFactory,
    StaffEmploymentAcademicYearFactory,
    StaffEmploymentFactory,
    StaffMemberFactory,
    StaffPositionFactory,
    WorkloadNormFactory,
)
from tests.factories.curriculum import (
    CurriculumDisciplineFactory,
    CurriculumFactory,
    CurriculumWorkloadFactory,
    DisciplineFactory,
    WorkloadTypeFactory,
)


__all__ = (
    "UserFactory",
    "StaffUserFactory",
    "SuperUserFactory",
    "UniversityFactory",
    "FacultyFactory",
    "DepartmentFactory",
    "SystemRoleFactory",
    "UserRoleAssignmentFactory",
    "AcademicYearFactory",
    "AcademicSemesterFactory",
    "EducationLevelFactory",
    "StudyFormFactory",
    "EducationDurationFactory",
    "StudyProgramFactory",
    "StudentGroupFactory",
    "StaffPositionFactory",
    "AcademicDegreeFactory",
    "AcademicTitleFactory",
    "StaffMemberFactory",
    "StaffEmploymentFactory",
    "StaffEmploymentAcademicYearFactory",
    "WorkloadNormFactory",
    "DisciplineFactory",
    "WorkloadTypeFactory",
    "CurriculumFactory",
    "CurriculumDisciplineFactory",
    "CurriculumWorkloadFactory",
)