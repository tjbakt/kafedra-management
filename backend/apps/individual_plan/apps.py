from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class IndividualPlanConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.individual_plan"
    verbose_name = _("Индивидуальные планы преподавателей")