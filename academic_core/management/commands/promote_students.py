# academic_core/management/commands/promote_students.py
from django.core.management.base import BaseCommand
from academic_core.models import Student
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Promote students annually based on joined_date (skeleton)'

    def handle(self, *args, **options):
        today = timezone.now().date()
        promoted = 0
        # Implement your graduation/promotion logic here.
        # This skeleton does not auto-modify grade fields (add grade field if you want).
        students = Student.objects.all()
        for s in students:
            # placeholder logic example:
            # if (today - s.joined_date).days >= 365:
            #    perform promotion action
            pass
        self.stdout.write(self.style.SUCCESS(f'Promote students script executed. examined={students.count()}'))
