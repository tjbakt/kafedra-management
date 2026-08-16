from django.db import migrations, models


WORKLOAD_TYPES = (
    {
        "code": "course_work_project_defense",
        "name_ru": "Защита курсовой работы/проекта",
        "name_uz": "Kurs ishi/loyihasini himoya qilish",
        "calculation_mode": "per_group",
        "report_category": "course_work_project_defense",
        "is_classroom": True,
        "is_teaching_load": True,
        "sort_order": 30,
    },
    {
        "code": "scientific_practice",
        "name_ru": "Научная практика",
        "name_uz": "Ilmiy amaliyot",
        "calculation_mode": "per_group",
        "report_category": "scientific_practice",
        "is_classroom": False,
        "is_teaching_load": True,
        "sort_order": 40,
    },
    {
        "code": "qualification_practice",
        "name_ru": "Квалификационная практика",
        "name_uz": "Malakaviy amaliyot",
        "calculation_mode": "per_group",
        "report_category": "qualification_practice",
        "is_classroom": False,
        "is_teaching_load": True,
        "sort_order": 50,
    },
    {
        "code": "master_dissertation_supervision",
        "name_ru": "Руководство магистерской диссертацией",
        "name_uz": "Magistrlik dissertatsiyasiga rahbarlik",
        "calculation_mode": "per_student",
        "report_category": "master_dissertation_supervision",
        "is_classroom": False,
        "is_teaching_load": True,
        "sort_order": 60,
    },
    {
        "code": "master_dissertation_defense",
        "name_ru": "Защита магистерской диссертации",
        "name_uz": "Magistrlik dissertatsiyasini himoya qilish",
        "calculation_mode": "per_student",
        "report_category": "master_dissertation_defense",
        "is_classroom": False,
        "is_teaching_load": True,
        "sort_order": 70,
    },
    {
        "code": "graduation_work_supervision",
        "name_ru": "Руководство выпускной квалификационной работой",
        "name_uz": "Bitiruv malakaviy ishiga rahbarlik",
        "calculation_mode": "per_student",
        "report_category": "graduation_work_supervision",
        "is_classroom": False,
        "is_teaching_load": True,
        "sort_order": 80,
    },
    {
        "code": "graduation_work_defense",
        "name_ru": "Защита выпускной квалификационной работы",
        "name_uz": "Bitiruv malakaviy ishini himoya qilish",
        "calculation_mode": "per_student",
        "report_category": "graduation_work_defense",
        "is_classroom": False,
        "is_teaching_load": True,
        "sort_order": 90,
    },
)


def create_missing_workload_types(apps, schema_editor):
    WorkloadType = apps.get_model(
        "curriculum",
        "WorkloadType",
    )

    for item in WORKLOAD_TYPES:
        WorkloadType.objects.get_or_create(
            code=item["code"],
            defaults={
                "name_ru": item["name_ru"],
                "name_uz": item["name_uz"],
                "calculation_mode": item["calculation_mode"],
                "report_category": item["report_category"],
                "is_classroom": item["is_classroom"],
                "is_teaching_load": item["is_teaching_load"],
                "is_active": True,
                "sort_order": item["sort_order"],
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ("curriculum", "0002_workloadtype_report_category"),
    ]

    operations = [
        migrations.AlterField(
            model_name="workloadtype",
            name="code",
            field=models.CharField(
                choices=[
                    ("lecture", "Лекции"),
                    ("practice", "Практические занятия"),
                    ("laboratory", "Лабораторные занятия"),
                    ("seminar", "Семинарские занятия"),
                    ("consultation", "Консультации"),
                    ("exam", "Экзамен"),
                    ("credit", "Зачёт"),
                    ("course_work", "Курсовая работа"),
                    ("course_project", "Курсовой проект"),
                    (
                        "course_work_project_defense",
                        "Защита курсовой работы/проекта",
                    ),
                    (
                        "scientific_practice",
                        "Научная практика",
                    ),
                    (
                        "qualification_practice",
                        "Квалификационная практика",
                    ),
                    (
                        "master_dissertation_supervision",
                        "Руководство магистерской диссертацией",
                    ),
                    (
                        "master_dissertation_defense",
                        "Защита магистерской диссертации",
                    ),
                    (
                        "graduation_work_supervision",
                        "Руководство выпускной квалификационной работой",
                    ),
                    (
                        "graduation_work_defense",
                        "Защита выпускной квалификационной работы",
                    ),
                    (
                        "independent_work",
                        "Самостоятельная работа",
                    ),
                    (
                        "other",
                        "Другой вид работы",
                    ),
                ],
                max_length=40,
                unique=True,
                verbose_name="Код",
            ),
        ),
        migrations.RunPython(
            create_missing_workload_types,
            migrations.RunPython.noop,
        ),
    ]