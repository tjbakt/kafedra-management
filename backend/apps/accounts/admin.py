from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "full_name_display",
        "email",
        "interface_language",
        "is_active",
        "is_staff",
    )
    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
        "interface_language",
        "groups",
    )
    search_fields = (
        "username",
        "first_name",
        "last_name",
        "middle_name",
        "email",
        "phone",
    )
    ordering = (
        "last_name",
        "first_name",
        "username",
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            _("Дополнительные данные"),
            {
                "fields": (
                    "middle_name",
                    "phone",
                    "avatar",
                    "interface_language",
                    "must_change_password",
                )
            },
        ),
        (
            _("Системная информация"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    @admin.display(description=_("Ф.И.О."))
    def full_name_display(self, obj):
        return obj.full_name or "—"