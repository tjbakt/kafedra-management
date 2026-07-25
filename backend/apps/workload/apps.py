from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class WorkloadConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.workload"
    verbose_name = _("Распределение учебной нагрузки")