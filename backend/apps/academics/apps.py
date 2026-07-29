from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AcademicsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.academics"
    verbose_name = _("Учебный процесс")

    def ready(self):
        # Импорт регистрирует обработчики signals.
        from apps.academics import signals  # noqa: F401