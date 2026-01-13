# core/notifications.py
from django.dispatch import Signal

fee_due = Signal()  # payload: {'student_id', 'amount', 'due_date'}
attendance_alert = Signal()  # payload: {'student_id','session_id','status'}
subject_assigned = Signal()  # payload: {'teacher_id','subject_id','assignment_id'}
session_created = Signal()
attendance_recorded = Signal()
