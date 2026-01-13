# academic_core/apps.py
from django.apps import AppConfig

class AcademicCoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'academic_core'

    def ready(self):
        # import signals to ensure they are registered
        try:
            import academic_core.signals  # noqa
        except Exception:
            pass
