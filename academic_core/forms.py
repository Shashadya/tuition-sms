# academic_core/forms.py
from django import forms
from django.forms import DateInput
from .models import (
    Teacher, TuitionClass, Subject, SubjectAssignment,
    Student, Guardian, Enrollment
)

# Shared date widget
DATE_WIDGET = DateInput(attrs={'type': 'date', 'class': 'form-control'})

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = [
            'title','first_name','last_name','profile_photo','dob',
            'phone','whatsapp','email','user','is_active'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'title': forms.Select(attrs={'class': 'form-control'}),
            'dob': DATE_WIDGET,
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class TuitionClassForm(forms.ModelForm):
    class Meta:
        model = TuitionClass
        fields = [
            'class_id','name','description','class_mode','fee_type',
            'per_session_fee','monthly_fee','class_teacher','capacity','active'
        ]
        widgets = {
            'class_id': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'class_mode': forms.Select(attrs={'class': 'form-control'}),
            'fee_type': forms.Select(attrs={'class': 'form-control'}),
            'per_session_fee': forms.NumberInput(attrs={'class': 'form-control'}),
            'monthly_fee': forms.NumberInput(attrs={'class': 'form-control'}),
            'class_teacher': forms.Select(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['subject_id','name','description']
        widgets = {
            'subject_id': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class SubjectAssignmentForm(forms.ModelForm):
    class Meta:
        model = SubjectAssignment
        fields = ['assign_id','subject','teacher','start_date','end_date','notes']
        widgets = {
            'assign_id': forms.TextInput(attrs={'class': 'form-control'}),
            'subject': forms.Select(attrs={'class': 'form-control'}),
            'teacher': forms.Select(attrs={'class': 'form-control'}),
            'start_date': DATE_WIDGET,
            'end_date': DATE_WIDGET,
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def clean(self):
        """
        Prevent creating a duplicate (subject, teacher) assignment.
        Allow updating the current instance without triggering the duplicate check.
        """
        cleaned = super().clean()
        subject = cleaned.get('subject')
        teacher = cleaned.get('teacher')

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'reg_no','profile_photo','first_name','last_name','dob','joined_date',
            'nic','school','gender','current_class','address','phone','whatsapp','email','is_active'
        ]
        widgets = {
            'reg_no': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'dob': DATE_WIDGET,
            'joined_date': DATE_WIDGET,
            'nic': forms.TextInput(attrs={'class': 'form-control'}),
            'school': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'current_class': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class GuardianForm(forms.ModelForm):
    class Meta:
        model = Guardian
        fields = ['name', 'relationship', 'phone', 'whatsapp', 'email', 'is_primary']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'relationship': forms.Select(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['student','tuition_class','start_date','end_date','active','fee_override']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'tuition_class': forms.Select(attrs={'class': 'form-control'}),
            'start_date': DATE_WIDGET,
            'end_date': DATE_WIDGET,
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'fee_override': forms.NumberInput(attrs={'class': 'form-control'}),
        }
