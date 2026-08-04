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
from tests.factories.teaching import (
    GroupCurriculumAssignmentFactory,
    GroupSemesterFactory,
    PlannedWorkloadFactory,
    TeachingStreamFactory,
    TeachingStreamGroupFactory,
)
from tests.factories.workload import (
    WorkloadDistributionFactory,
)
from tests.factories.individual_plan import (
    IndividualActivityTypeFactory,
    IndividualPlanFactory,
    IndividualPlanItemFactory,
    IndividualPlanSectionFactory,
    IndividualPlanTeachingWorkloadFactory,
)
from tests.factories.audit import (
    AuditEventFactory,
)
from tests.factories.notifications import (
    NotificationFactory,
    UserTaskFactory,
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
    "GroupCurriculumAssignmentFactory",
    "GroupSemesterFactory",
    "TeachingStreamFactory",
    "TeachingStreamGroupFactory",
    "PlannedWorkloadFactory",
    "WorkloadDistributionFactory",
    "IndividualPlanSectionFactory",
    "IndividualActivityTypeFactory",
    "IndividualPlanFactory",
    "IndividualPlanItemFactory",
    "IndividualPlanTeachingWorkloadFactory",
    "NotificationFactory",
    "UserTaskFactory",
    "AuditEventFactory",
)