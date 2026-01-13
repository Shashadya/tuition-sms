# academic_core/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SubjectAssignment
from core.notifications import subject_assigned

@receiver(post_save, sender=SubjectAssignment)
def on_subject_assignment_created(sender, instance, created, **kwargs):
    if created:
        payload = {
            'teacher_id': instance.teacher_id,
            'subject_id': instance.subject_id,
            'assignment_id': instance.pk
        }
        # send lightweight signal; receivers implemented in other apps
        subject_assigned.send(sender=sender, **payload)
