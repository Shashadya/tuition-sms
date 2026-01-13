# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin for the project's custom User model.

    Behaviour:
    - Displays role, staff/superuser flags, and allows editing role in admin.
    - When saving a user via admin: if role == 'admin' then is_staff=True (so admin can access /admin/)
      otherwise if role == 'staff' we ensure is_staff=False to avoid giving card markers admin access.
    """

    list_display = ('username', 'email', 'get_full_name', 'role', 'is_staff', 'is_superuser', 'is_active')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

    fieldsets = (
        ("Login Credentials", {"fields": ("username", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "email")}),
        ("Role & Permissions", {"fields": ("role", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "role", "password1", "password2"),
        }),
    )

    def get_full_name(self, obj):
        name = obj.get_full_name()
        return name or "-"
    get_full_name.short_description = "Name"

    def save_model(self, request, obj, form, change):
        """
        Enforce staff flag semantics:
        - role == 'admin' -> ensure is_staff True
        - role == 'staff'  -> ensure is_staff False (card markers should not access Django admin)
        Superusers remain superusers.
        """
        try:
            role = getattr(obj, 'role', None)
            # If role indicates an administrator, ensure they have is_staff set
            if role == getattr(User, 'ROLE_ADMIN', 'admin'):
                obj.is_staff = True
            else:
                # If role is staff/cardmarker, ensure is_staff is False to avoid accidental admin access
                if role == getattr(User, 'ROLE_STAFF', 'staff'):
                    obj.is_staff = False
                # otherwise leave is_staff as the admin chose it (helpful for superusers)
        except Exception:
            pass

        super().save_model(request, obj, form, change)
