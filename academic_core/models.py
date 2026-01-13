# academic_core/models.py
from django.conf import settings
from django.db import models
from django.utils import timezone
from decimal import Decimal

# -----------------------------------
# TEACHER MODEL
# -----------------------------------

TITLE_CHOICES = [
    ('mr', 'Mr.'),
    ('ms', 'Ms.'),
    ('mrs', 'Mrs.'),
    ('rev', 'Rev.'),
]

class Teacher(models.Model):
    title = models.CharField(max_length=10, choices=TITLE_CHOICES, default='mr')
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    profile_photo = models.ImageField(upload_to='teachers/photos/', null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=32, blank=True)
    whatsapp = models.CharField(max_length=32, blank=True)
    email = models.EmailField(blank=True, null=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teacher_profile'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.title} {self.first_name} {self.last_name}"


# -----------------------------------
# TUITION CLASS MODEL
# -----------------------------------

CLASS_MODE_CHOICES = [
    ('group', 'Group'),
    ('one_to_one', 'One-to-one'),
    ('online', 'Online'),
    ('home', 'Home'),
]

FEE_TYPE_CHOICES = [
    ('per_session', 'Per session'),
    ('monthly', 'Monthly'),
    ('term', 'Per term'),
]

class TuitionClass(models.Model):
    class_id = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    class_mode = models.CharField(max_length=20, choices=CLASS_MODE_CHOICES, default='group')
    fee_type = models.CharField(max_length=20, choices=FEE_TYPE_CHOICES, default='per_session')
    per_session_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    class_teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tuition_classes'
    )
    capacity = models.PositiveIntegerField(default=10)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['class_id']

    def __str__(self):
        return f"{self.class_id} - {self.name}"


# -----------------------------------
# SUBJECT MODEL
# -----------------------------------

class Subject(models.Model):
    subject_id = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['subject_id']

    def __str__(self):
        return f"{self.subject_id} - {self.name}"


# -----------------------------------
# SUBJECT ASSIGNMENT MODEL
# -----------------------------------

class SubjectAssignment(models.Model):
    assign_id = models.CharField(max_length=60, unique=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assignments')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='assignments')
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['subject', 'teacher'], name='unique_subject_teacher')
        ]
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.assign_id}: {self.subject.name} -> {self.teacher.first_name} {self.teacher.last_name}"


# -----------------------------------
# STUDENT MODEL
# -----------------------------------

GENDER_CHOICES = [
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
]

class Student(models.Model):
    reg_no = models.CharField(max_length=30, unique=True)  # Student ID
    profile_photo = models.ImageField(upload_to='students/photos/', null=True, blank=True)
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    dob = models.DateField(null=True, blank=True)
    joined_date = models.DateField(default=timezone.now)
    nic = models.CharField(max_length=30, blank=True)
    school = models.CharField(max_length=200, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    current_class = models.ForeignKey(
        TuitionClass,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='students'
    )
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=32, blank=True)
    whatsapp = models.CharField(max_length=32, blank=True)
    email = models.EmailField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['reg_no']

    def __str__(self):
        return f"{self.reg_no} - {self.first_name} {self.last_name}"


# -----------------------------------
# GUARDIAN MODEL (normalized choice keys)
# -----------------------------------

REL_CHOICES = [
    ('mother', 'Mother'),
    ('father', 'Father'),
    ('guardian', 'Guardian'),
    ('other', 'Other'),
]

class Guardian(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='guardians')
    name = models.CharField(max_length=200)
    relationship = models.CharField(max_length=20, choices=REL_CHOICES)
    phone = models.CharField(max_length=32, blank=True)
    whatsapp = models.CharField(max_length=32, blank=True)
    email = models.EmailField(blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', 'name']
        verbose_name = "Guardian"
        verbose_name_plural = "Guardians"

    def __str__(self):
        return f"{self.name} ({self.relationship}) - {self.student.reg_no}"


# -----------------------------------
# ENROLLMENT MODEL
# -----------------------------------

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    tuition_class = models.ForeignKey(TuitionClass, on_delete=models.CASCADE, related_name='enrollments')
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    active = models.BooleanField(default=True)
    fee_override = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ('student', 'tuition_class', 'start_date')
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.student.reg_no} -> {self.tuition_class.class_id} ({'active' if self.active else 'inactive'})"
