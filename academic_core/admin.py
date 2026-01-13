# academic_core/admin.py
from django.contrib import admin
from .models import Teacher, TuitionClass, Subject, SubjectAssignment, Student, Guardian, Enrollment

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('title','first_name','last_name','phone','email','is_active')
    search_fields = ('first_name','last_name','email','phone')
    list_filter = ('is_active',)

@admin.register(TuitionClass)
class TuitionClassAdmin(admin.ModelAdmin):
    list_display = ('class_id','name','class_teacher','class_mode','fee_type','per_session_fee','monthly_fee','capacity','active')
    search_fields = ('class_id','name')
    raw_id_fields = ('class_teacher',)
    list_filter = ('class_mode','fee_type','active')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('subject_id','name')
    search_fields = ('subject_id','name')

@admin.register(SubjectAssignment)
class SubjectAssignmentAdmin(admin.ModelAdmin):
    list_display = ('assign_id', 'subject', 'teacher', 'start_date', 'end_date')
    search_fields = ('assign_id', 'subject__name', 'teacher__first_name', 'teacher__last_name')
    list_filter = ('start_date', 'end_date')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('reg_no','first_name','last_name','current_class','phone','email','is_active')
    search_fields = ('reg_no','first_name','last_name','email')
    list_filter = ('current_class','is_active')

@admin.register(Guardian)
class GuardianAdmin(admin.ModelAdmin):
    list_display = ('name','relationship','student','phone','is_primary')
    search_fields = ('name','student__reg_no')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student','tuition_class','start_date','active')
    search_fields = ('student__reg_no','tuition_class__class_id')
    list_filter = ('active','tuition_class')

